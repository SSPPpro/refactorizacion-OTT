import os
import json
import geopandas as gpd
from sentinelhub import BBox, CRS, MimeType
from src.models import DownloadPolygonResult
from src.services.download_vectorizer import DownloadVectorizer


class DownloadPolygonService:
    """
    Main service to download raster data and vectorize polygons from Sentinel Hub.
    Saves TIFFs in 'results/raster/' and vector files in 'results/vector/'.
    """

    def __init__(self, configurator, evalscript_generator, download_client, raster_processor,
                 output_folder="results", resolution=10):
        self.configurator = configurator
        self.evalscript_generator = evalscript_generator
        self.download_client = download_client
        self.raster_processor = raster_processor
        self.output_folder = output_folder
        self.resolution = resolution

        # Create folders
        os.makedirs(self.output_folder, exist_ok=True)
        self.raster_folder = os.path.join(self.output_folder, "raster")
        self.vector_folder = os.path.join(self.output_folder, "vector")

        os.makedirs(self.raster_folder, exist_ok=True)
        os.makedirs(self.vector_folder, exist_ok=True)

        # Optional: clean only raster folder before each run
        for f in os.listdir(self.raster_folder):
            os.remove(os.path.join(self.raster_folder, f))


    def process_polygons(self, aoi_geojson: str, start_date: str, end_date: str,
                         index_name: str = "NDVI", threshold: float = 0.2):
        print("[DownloadPolygonService] Starting polygon download and vectorization pipeline...")

        try:
            # --- 1️ Load AOI ---
            if not os.path.exists(aoi_geojson):
                raise FileNotFoundError(f"AOI file not found at {aoi_geojson}")

            with open(aoi_geojson, "r", encoding="utf-8") as f:
                geojson_data = json.load(f)

            coords = geojson_data["features"][0]["geometry"]["coordinates"][0]
            lons, lats = zip(*coords)
            aoi_bbox = BBox(bbox=[min(lons), min(lats), max(lons), max(lats)], crs=CRS.WGS84)
            bbox_list = [aoi_bbox]

            # --- 2️ Evalscript for index ---
            evalscript = self.evalscript_generator.get_evalscript(index_name)
            if not evalscript:
                raise ValueError(f"No evalscript found for index: {index_name}")

            # --- 3️ Download TIFF ---
            print("[DownloadPolygonService] Downloading raster data...")
            downloaded_files = self.download_client.download_data(
                bbox_list=bbox_list,
                evalscript=evalscript,
                start_date=start_date,
                end_date=end_date,
                output_folder=self.raster_folder,
                resolution=self.resolution,
                mime_type=MimeType.TIFF
            )

            if not downloaded_files:
                raise Exception("No raster files were downloaded.")

            # --- 4️ Create mosaic ---
            print("[DownloadPolygonService] Creating raster mosaic...")
            arr, transform, crs, tiff_output_path = self.raster_processor.create_mosaic(
                downloaded_files,
                self.raster_folder,
                index_name
            )

            if arr is None:
                raise Exception("Failed to create raster mosaic.")

            # --- 5️ Vectorize ---
            print("[DownloadPolygonService] Vectorizing raster data...")
            vectorizer = DownloadVectorizer(
                configurator=self.configurator,
                evalscript_generator=self.evalscript_generator,
                download_client=self.download_client,
                raster_processor=self.raster_processor,
                output_folder=self.vector_folder,
                resolution=self.resolution
            )

            gdf, shapefile_output_path = vectorizer.vectorize(
                (arr, transform, crs),
                index_name=index_name,
                output_folder=self.vector_folder,
                threshold=threshold
            )

            # --- 6️ Save summary JSON ---
            response_path = os.path.join(self.output_folder, "response.json")
            summary_data = {
                "start_date": start_date,
                "end_date": end_date,
                "tiff_path": tiff_output_path,
                "shapefile_path": shapefile_output_path,
                "geojson_path": os.path.join(self.vector_folder, f"{index_name}_vectorized.geojson")
            }

            with open(response_path, "w", encoding="utf-8") as f:
                json.dump(summary_data, f, indent=4)

            print(f"[DownloadPolygonService] Summary saved to: {response_path}")

            return DownloadPolygonResult(
                polygons_gdf=gdf,
                start_date=start_date,
                end_date=end_date,
                aoi_geojson_path=aoi_geojson,
                tiff_output_path=tiff_output_path,
                shapefile_output_path=shapefile_output_path
            )

        except Exception as e:
            print(f" Error in DownloadPolygonService: {e}")
            return DownloadPolygonResult(error=str(e))
