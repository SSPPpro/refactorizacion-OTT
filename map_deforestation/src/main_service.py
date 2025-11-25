import os
import json
import geopandas as gpd
from sentinelhub import BBox, CRS
from src.models import DeforestationResult

class DeforestationService:
    def __init__(self, configurator, evalscript_gen, download_client, raster_proc, vectorizer, output_folder="results"):
        self.evalscript_gen = evalscript_gen
        self.download_client = download_client
        self.raster_proc = raster_proc
        self.vectorizer = vectorizer
        self.output_folder = output_folder
        
        self.raster_folder = os.path.join(output_folder, "raster")
        self.vector_folder = os.path.join(output_folder, "vector")
        os.makedirs(self.raster_folder, exist_ok=True)
        os.makedirs(self.vector_folder, exist_ok=True)

    def process_deforestation(self, aoi_path: str, start_date: str, end_date: str, threshold: float = 0.1):
        try:
            # 1. Load AOI
            if not os.path.exists(aoi_path):
                raise FileNotFoundError(f"AOI no encontrado: {aoi_path}")

            with open(aoi_path, "r", encoding='utf-8') as f:
                data = json.load(f)
            
            coords = data["features"][0]["geometry"]["coordinates"][0]
            lons, lats = zip(*coords)
            bbox = BBox(bbox=[min(lons), min(lats), max(lons), max(lats)], crs=CRS.WGS84)

            # 2. Get Evalscript
            script = self.evalscript_gen.get_evalscript("DEFORESTATION", threshold=threshold)

            # 3. Download
            print("⬇ Downloading Sentinel-2 data...")
            files = self.download_client.download_data(
                bbox_list=[bbox],
                evalscript=script,
                start_date=start_date,
                end_date=end_date,
                output_folder=self.raster_folder,
                resolution=10 
            )

            # 4. Mosaic
            print(" Processing raster...")
            arr, transform, crs, tiff_path = self.raster_proc.create_mosaic(files, self.raster_folder, "deforestation")

            # 5. Vectorize
            print(" Vectorizing results...")
            # --- MODIFICADO: Pasamos start_date y end_date ---
            gdf, shp_path = self.vectorizer.vectorize(
                (arr, transform, crs), 
                "deforestation", 
                self.vector_folder,
                start_date=start_date, # Nuevo argumento
                end_date=end_date      # Nuevo argumento
            )

            return DeforestationResult(
                polygons_gdf=gdf,
                start_date=start_date,
                end_date=end_date,
                tiff_output_path=tiff_path,
                shapefile_output_path=shp_path
            )

        except Exception as e:
            return DeforestationResult(error=str(e))