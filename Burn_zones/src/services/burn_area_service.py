import os
from typing import List
import numpy as np
import geopandas as gpd
import rasterio as rio
from rasterio import features
from shapely.geometry import shape
from src.interfaces import IBurnAreaService

class BurnAreaService(IBurnAreaService):
    """Convierte TIFFs binarios (1=quemado) a GeoJSON / GeoDataFrame"""

    def tiffs_to_geojson(self, tiff_paths: List[str], out_geojson: str) -> str:
        polygons = []
        src_crs = None

        for tif in tiff_paths:
            with rio.open(tif) as src:
                arr = src.read(1)
                transform = src.transform
                src_crs = src.crs
                mask = arr == 1
                for geom, value in features.shapes(arr.astype(np.int16), mask=mask, transform=transform):
                    if value == 1:
                        polygons.append({"geometry": shape(geom), "state": "Quemado"})

        if not polygons:
            raise ValueError("No se detectaron áreas quemadas en los TIFFs proporcionados.")

        gdf = gpd.GeoDataFrame(polygons, crs=src_crs)
        # convertir a EPSG:4326 para interoperabilidad
        try:
            gdf = gdf.to_crs("EPSG:4326")
        except Exception:
            # si ya está en EPSG:4326 puede fallar; ignoramos
            pass

        dissolved = gdf.dissolve(by="state", as_index=False)

        os.makedirs(os.path.dirname(out_geojson) or ".", exist_ok=True)
        dissolved.to_file(out_geojson, driver="GeoJSON")
        return out_geojson
