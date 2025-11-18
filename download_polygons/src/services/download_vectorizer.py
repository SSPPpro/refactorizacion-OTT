import os
import numpy as np
import geopandas as gpd
import rasterio as rio
from rasterio import features
from shapely.geometry import shape
from typing import Tuple
from src.interfaces import IVectorizer


class DownloadVectorizer(IVectorizer):
    def __init__(self, configurator, evalscript_generator, download_client, raster_processor,
                 output_folder="results/vector", resolution=10):
        self.configurator = configurator
        self.evalscript_generator = evalscript_generator
        self.download_client = download_client
        self.raster_processor = raster_processor
        self.output_folder = output_folder
        self.resolution = resolution

    def vectorize(self, raster_data_tuple: Tuple[np.ndarray, rio.transform.Affine, rio.crs.CRS],
                  index_name: str, output_folder: str, threshold: float = None) -> Tuple[gpd.GeoDataFrame, str]:
        """
        Vectorizes raster data into polygons.
        Saves both GeoJSON and Shapefile in 'vector/' folder.
        """
        arr, transform, crs = raster_data_tuple

        if arr is None or arr.size == 0:
            print("[DownloadVectorizer] Empty raster data received.")
            return gpd.GeoDataFrame(), None

        print(f"[DownloadVectorizer] Converting raster data to polygons for index {index_name}...")
        gdf = self.raster_processor.classify_from_array(arr, transform, crs, index_name)

        if gdf is None or gdf.empty:
            print("[DownloadVectorizer] No polygons generated from raster.")
            return gpd.GeoDataFrame(), None

        os.makedirs(output_folder, exist_ok=True)

        base_filename = f"{index_name}_vectorized"

        # Save GeoJSON
        geojson_output_path = os.path.join(output_folder, f"{base_filename}.geojson")
        gdf.to_file(geojson_output_path, driver="GeoJSON")
        print(f"[DownloadVectorizer] GeoJSON saved at: {geojson_output_path}")

        # Save Shapefile
        shapefile_output_path = os.path.join(output_folder, f"{base_filename}.shp")
        gdf_for_shp = gdf.copy()
        gdf_for_shp.rename(columns={
            "IndexState": "State",
            "IndexRange": "Range",
            "IndexRangeMean": "MeanRange",
            "IndexName": "IdxName"
        }, inplace=True)
        gdf_for_shp.to_file(shapefile_output_path, driver="ESRI Shapefile")
        print(f"[DownloadVectorizer] Shapefile saved at: {shapefile_output_path}")

        return gdf, shapefile_output_path
