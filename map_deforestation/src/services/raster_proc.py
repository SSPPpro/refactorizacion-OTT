import os
import numpy as np
import rasterio
from rasterio import features
from rasterio.merge import merge
from shapely.geometry import shape
import geopandas as gpd
from typing import List, Tuple
from src.interfaces import IRasterProcessor

class RasterProcessor(IRasterProcessor):
    
    CLASSIFICATION_MAP = {
        "deforestation": {
            1: ["Deforestado", "Pérdida significativa de vegetación"]
        }
    }

    def create_mosaic(self, tiff_paths: List[str], output_folder: str, prefix: str) -> Tuple[np.ndarray, rasterio.transform.Affine, rasterio.crs.CRS, str]:
        if not tiff_paths:
            return None, None, None, None

        output_tiff_path = os.path.join(output_folder, f"{prefix}_mosaic.tif")
        srcs = [rasterio.open(fp) for fp in tiff_paths]
        
        if len(srcs) == 1:
            arr = srcs[0].read(1)
            transform, crs = srcs[0].transform, srcs[0].crs
            with rasterio.open(output_tiff_path, 'w', driver='GTiff', 
                               height=srcs[0].height, width=srcs[0].width, count=1, 
                               dtype=arr.dtype, crs=crs, transform=transform) as dst:
                dst.write(arr, 1)
        else:
            mosaic, out_trans = merge(srcs)
            arr = mosaic[0]
            transform, crs = out_trans, srcs[0].crs
            with rasterio.open(output_tiff_path, 'w', driver='GTiff', 
                               height=arr.shape[0], width=arr.shape[1], count=1, 
                               dtype=arr.dtype, crs=crs, transform=transform) as dst:
                dst.write(arr, 1)

        for s in srcs:
            s.close()
        # Opcional: limpieza de archivos individuales descargados
            
        return arr, transform, crs, output_tiff_path

    def classify_from_array(self, arr: np.ndarray, transform: rasterio.transform.Affine, crs: rasterio.crs.CRS, index_name: str) -> gpd.GeoDataFrame:
        
        # Filtramos solo donde valor es 1 (Deforestación)
        # Convertir a uint8 si no lo es, para ahorrar memoria
        arr = arr.astype(np.uint8)
        mask = arr == 1 
        
        if not np.any(mask):
            return gpd.GeoDataFrame()

        shapes_gen = features.shapes(arr, mask=mask, transform=transform)

        features_list = []
        class_info = self.CLASSIFICATION_MAP.get("deforestation", {})

        for geom, val in shapes_gen:
            val_int = int(val)
            if val_int == 0: continue 

            state_desc = class_info.get(val_int, ["Sin clasificación", ""])[0]
            
            features_list.append({
                "geometry": shape(geom),
                "properties": {
                    "value": val_int,
                    "state": state_desc,
                    "type": "Deforestación"
                }
            })

        if not features_list:
            return gpd.GeoDataFrame()

        gdf = gpd.GeoDataFrame.from_features(features_list, crs=crs)
        
        # Disolver geometrías contiguas
        dissolved = gdf.dissolve(by="value", as_index=False).to_crs(epsg=4326)
        
        return dissolved