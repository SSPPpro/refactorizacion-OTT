import os
import numpy as np
import geopandas as gpd
from typing import Tuple
from src.interfaces import IVectorizer

class DeforestationVectorizer(IVectorizer):
    def __init__(self, raster_processor, output_folder="results/vector"):
        self.raster_processor = raster_processor
        self.output_folder = output_folder

    def vectorize(self, raster_data_tuple: Tuple, index_name: str, output_folder: str, start_date: str = None, end_date: str = None) -> Tuple[gpd.GeoDataFrame, str]:
        arr, transform, crs = raster_data_tuple

        print(f"[DeforestationVectorizer] Vectorizing deforestation data...")
        gdf = self.raster_processor.classify_from_array(arr, transform, crs, "deforestation")

        if gdf.empty:
            print("[DeforestationVectorizer] No deforestation detected.")
            return gdf, None

        # --- NUEVO: Agregar atributos de fecha ---
        if start_date:
            gdf["StartDate"] = start_date
        if end_date:
            gdf["EndDate"] = end_date
        # ----------------------------------------

        os.makedirs(output_folder, exist_ok=True)
        base_filename = "deforestation_detected"

        geojson_path = os.path.join(output_folder, f"{base_filename}.geojson")
        gdf.to_file(geojson_path, driver="GeoJSON")
        
        shp_path = os.path.join(output_folder, f"{base_filename}.shp")
        gdf.to_file(shp_path, driver="ESRI Shapefile")

        return gdf, shp_path