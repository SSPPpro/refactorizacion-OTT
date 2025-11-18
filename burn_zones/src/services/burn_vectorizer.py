from typing import Optional
import numpy as np
import geopandas as gpd
import rasterio as rio
import os
from rasterio import features
from shapely.geometry import shape
from src.interfaces import IVectorizer


class BurnAreaVectorizer(IVectorizer):
    """
    Vectorizador de áreas quemadas.
    Convierte el ráster binario (0/1) en polígonos y agrega metadatos:
    value, State, Class, IdxName, StartDate, EndDate.
    Guarda shapefile en 'vector/' y geojson en 'results/'.
    """

    def vectorize_burn_areas(
        self,
        burn_area_tif_path: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> gpd.GeoDataFrame:
        """Procesa el TIFF binario (0/1) y genera un GeoDataFrame con atributos estándar."""

        if not burn_area_tif_path or not os.path.exists(burn_area_tif_path):
            print(" No se encontró el archivo TIFF de áreas quemadas para procesar.")
            return gpd.GeoDataFrame()

        try:
            with rio.open(burn_area_tif_path) as src:
                raster_data = src.read(1)
                transform = src.transform
                crs = src.crs

                raster_data = np.nan_to_num(raster_data, nan=0).astype(np.uint8)

                polygons = []
                for geom, value in features.shapes(raster_data, mask=(raster_data >= 0), transform=transform):
                    polygons.append({"geometry": shape(geom), "value": int(value)})

            if not polygons:
                print(" No se encontraron polígonos para vectorizar.")
                return gpd.GeoDataFrame()

            gdf = gpd.GeoDataFrame(polygons, crs=crs)

            #  Filtrar solo polígonos quemados (value = 1)
            gdf = gdf[gdf["value"] == 1].copy()

            if gdf.empty:
                print(" No hay píxeles con valor 1 (quemados).")
                return gpd.GeoDataFrame()

            # Asignar atributos estándar
            gdf["State"] = "Burned"
            gdf["Class"] = "Quemado"
            gdf["IdxName"] = "NBR"
            gdf["StartDate"] = start_date or ""
            gdf["EndDate"] = end_date or ""

            gdf = gdf.to_crs(epsg=4326)

            # --- Rutas de salida ---
            results_folder = os.path.abspath(os.path.join(os.path.dirname(burn_area_tif_path), os.pardir))
            vector_folder = os.path.join(results_folder, "vector")
            os.makedirs(vector_folder, exist_ok=True)

            shp_path = os.path.join(vector_folder, "burn_areas_with_fields.shp")
            geojson_path = os.path.join(results_folder, f"burnt_areas_{start_date}_{end_date}.geojson")

            # --- Guardar archivos ---
            gdf.to_file(shp_path, driver="ESRI Shapefile")
            gdf.to_file(geojson_path, driver="GeoJSON")

            print(f" Shapefile guardado en: {shp_path}")
            print(f" GeoJSON guardado en: {geojson_path}")

            return gdf

        except Exception as e:
            print(f" Error durante la vectorización de áreas quemadas: {e}")
            return gpd.GeoDataFrame()
