import os
import numpy as np
import rasterio
from rasterio import features
import geopandas as gpd
from shapely.geometry import shape
from rasterio.merge import merge
from typing import List, Tuple
from abc import ABC, abstractmethod

from src.interfaces import IRasterProcessor


class BaseRasterProcessor(IRasterProcessor, ABC):
    """
    Clase base abstracta que define el contrato para procesadores raster.
    """

    @abstractmethod
    def create_mosaic(self, tiff_paths: List[str], output_folder: str, index_name: str) -> Tuple[np.ndarray, rasterio.transform.Affine, rasterio.crs.CRS, str]:
        pass

    @abstractmethod
    def classify_from_array(self, arr: np.ndarray, transform: rasterio.transform.Affine, crs: rasterio.crs.CRS, index_name: str) -> gpd.GeoDataFrame:
        pass


class RasterProcessor(BaseRasterProcessor):
    """
    Implementación concreta del procesador raster que:
    - Lee uno o varios GeoTIFFs.
    - Crea mosaico si hay más de uno, devolviendo la tupla (array, transform, crs, tiff_output_path).
    - Reclasifica según el índice y devuelve un GeoDataFrame disuelto por clases.
    """

    combined_state = {
      "ndvi": {1: ["Ausencia de vegetación o cobertura vegetal muy escasa", "< 0"], 2: ["Vegetación escasa o estresada","0 - 0.2"], 3: ["Vegetación en condiciones moderadas","0.2 - 0.5"], 4: ["Vegetación densa y saludable","0.5 - 0.8"], 5: ["Vegetación extremadamente densa y saludable","0.8 - 1"]},
      "gndvi": {1:["Áreas con baja o nula vegetación, suelos desnudos, agua o superficies construidas","< 0"],2:["Vegetación en condiciones saludables, pero no particularmente densa","0 - 0.5"],3:["Vegetación densa y saludable","0.5 - 0.8"],4:["Vegetación extremadamente densa y saludable","0.8 - 1"]},
      "evi": {1:["Zonas con muy poca o ninguna vegetacion","< 0"],2:["Presencia creciente de vegetacion","0 - 0.5"],3:["Vegetacion mas densa y saludable que las areas verdes","0.5 - 0.8"],4:["Vegetacion con la maxima densidad y salud de la vegetación","0.8 - 1"]},
      "savi": {1:["Muy baja vegetacion o suelo expuesto","< 0"],2:["Vegetación escasa","0 - 0.5"],3:["Vegetación moderada","0.5 - 0.8"],4:["Vegetación extremadamente densa","0.8 - 1"]},
      "ndci": {1:["Vegetacion con baja concentacion de clorofila","< 0"],2:["Vegetación con concentracion de clorofila moderada","0 - 0.2"],3:["Vegetacion con alta concentacion de clorofila","0.2 - 1"]},
      "ndmi": {1:["Baja humedad en la vegetación","< 0"],2:["Moderada humedad en la vegetacion","0 - 0.5"],3:["Alta humedad en la vegetación","0.5 - 0.8"],4:["Muy alta humedad en la vegetación","0.8 - 1"]},
      "ndsi": {1:["Zonas Ausencia de Nieve","< 0"],2:["Zonas con poca nieve","0 - 0.4"],3:["Zonas con nieve densa","0.4 - 1"]},
      "ndwi": {1:["Zonas sin presencia de agua","< 0"],2:["Zonas inundadas","0 - 1"]},
      "ndbi": {1:["baja presencia de superficies construidas o una alta presencia de vegetación y áreas naturales","< -0.05"],2:["Zonas construidas con vegetación","-0.05 - 0.05"],3:["Zonas con alta construccion","0.05 - 1"]},
      "nbr": {1:["Zonas no quemadas","< 0.1"],2:["Zonas quemadas con gravedad moderada baja","0.1 - 0.44"],3:["Zonas quemadas con gravedad moderada alta","0.44 - 0.66"],4:["Zonas gravemente quemadas","0.66 - 1"]}
    }

    def create_mosaic(self, tiff_paths: List[str], output_folder: str, index_name: str) -> Tuple[np.ndarray, rasterio.transform.Affine, rasterio.crs.CRS, str]:
        """
        Crea un mosaico a partir de múltiples GeoTIFFs o retorna el único raster.
        Devuelve una tupla (array, transform, crs, tiff_output_path) directamente.
        """
        if not tiff_paths:
            print("[RasterProcessor] No se proporcionaron rutas de TIFF para crear el mosaico.")
            return None, None, None, None

        srcs = [rasterio.open(fp) for fp in tiff_paths]
        
        if len(srcs) == 0:
            for s in srcs:
                s.close()
            return None, None, None, None # No hay archivos para procesar

        if len(srcs) == 1:
            src = srcs[0]
            arr = src.read(1).astype(np.float32)
            transform, crs = src.transform, src.crs
            output_tiff_path = os.path.join(output_folder, f"{index_name}_index.tif")
            # Guardar el TIFF original si solo hay uno, para conservarlo
            with rasterio.open(output_tiff_path, 'w',
                                driver='GTiff',
                                height=src.height,
                                width=src.width,
                                count=1,
                                dtype=arr.dtype,
                                crs=crs,
                                transform=transform) as dst:
                dst.write(arr, 1)
            print(f"[RasterProcessor] Archivo TIFF del índice guardado en: {output_tiff_path}")
            src.close() # Cerrar el archivo original
            # Eliminar el archivo temporal descargado si es diferente al guardado
            if os.path.abspath(src.name) != os.path.abspath(output_tiff_path):
                try:
                    os.remove(src.name)
                    print(f"[RasterProcessor] Archivo temporal {src.name} eliminado.")
                except OSError as e:
                    print(f"[RasterProcessor] Error al eliminar archivo {src.name}: {e}")

        else:
            mosaic, out_trans = merge(srcs)
            arr = mosaic[0].astype(np.float32)
            transform, crs = out_trans, srcs[0].crs
            output_tiff_path = os.path.join(output_folder, f"{index_name}_mosaic_index.tif")
            # Guardar el mosaico
            with rasterio.open(output_tiff_path, 'w',
                                driver='GTiff',
                                height=arr.shape[0],
                                width=arr.shape[1],
                                count=1,
                                dtype=arr.dtype,
                                crs=crs,
                                transform=transform) as dst:
                dst.write(arr, 1)
            print(f"[RasterProcessor] Mosaico del índice guardado en: {output_tiff_path}")
            
            # Eliminar los archivos TIFF originales descargados (temporales)
            for s in srcs:
                s.close()
                try:
                    os.remove(s.name)
                    print(f"[RasterProcessor] Archivo descargado temporal {s.name} eliminado.")
                except OSError as e:
                    print(f"[RasterProcessor] Error al eliminar archivo {s.name}: {e}")

        return arr, transform, crs, output_tiff_path

    def _reclass_func(self, idx: str):
        """Devuelve una función lambda para reclasificar valores según el índice."""
        if not isinstance(idx, str):
            print(f"ADVERTENCIA: 'idx' en _reclass_func debe ser una cadena, se recibió {type(idx).__name__}. Devolviendo función nula.")
            return lambda x: None
        
        k = idx.lower()
        if k == "ndvi":
            return lambda x: None if np.isnan(x) else (1 if x < 0 else (2 if x <= 0.2 else (3 if x <= 0.5 else (4 if x <= 0.8 else 5))))
        if k == "gndvi":
            return lambda x: None if np.isnan(x) else (1 if x < 0 else (2 if x <= 0.5 else (3 if x <= 0.8 else 4)))
        if k == "evi":
            return lambda x: None if np.isnan(x) else (1 if x < 0 else (2 if x <= 0.5 else (3 if x <= 0.8 else 4)))
        if k == "savi":
            return lambda x: None if np.isnan(x) else (1 if x < 0 else (2 if x <= 0.5 else (3 if x <= 0.8 else 4)))
        if k == "ndci":
            return lambda x: None if np.isnan(x) else (1 if x < 0 else (2 if x <= 0.2 else 3))
        if k == "ndmi":
            return lambda x: None if np.isnan(x) else (1 if x < 0 else (2 if x <= 0.5 else (3 if x <= 0.8 else 4)))
        if k == "ndsi":
            return lambda x: None if np.isnan(x) else (1 if x < 0 else (2 if x <= 0.45 else 3))
        if k == "ndwi":
            return lambda x: None if np.isnan(x) else (1 if x < 0 else 2)
        if k == "ndbi":
            return lambda x: None if np.isnan(x) else (1 if x <= -0.05 else (2 if x <= 0.05 else 3))
        if k == "nbr":
            return lambda x: None if np.isnan(x) else (1 if x <= 0.1 else (2 if x <= 0.44 else (3 if x <= 0.66 else 4)))
        return lambda x: None

    def classify_from_array(self, arr: np.ndarray, transform: rasterio.transform.Affine, crs: rasterio.crs.CRS, index_name: str) -> gpd.GeoDataFrame:
        """Procesa un array raster, lo reclasifica y devuelve un GeoDataFrame disuelto."""
        if arr is None or transform is None or crs is None:
            print("[RasterProcessor] Datos raster incompletos para clasificar.")
            return gpd.GeoDataFrame()

        # Asegurar que index_name sea una cadena antes de usarlo
        if not isinstance(index_name, str):
            raise TypeError(f"El argumento 'index_name' en classify_from_array debe ser una cadena, pero se recibió un {type(index_name).__name__}.")

        reclass = self._reclass_func(index_name)
        flat = arr.ravel()
        reclass_flat = np.zeros_like(flat, dtype=np.int16)
        index_groups = {}

        for i, v in enumerate(flat):
            if np.isnan(v):
                reclass_flat[i] = 0
            else:
                cls = reclass(v)
                if cls is None:
                    reclass_flat[i] = 0
                else:
                    reclass_flat[i] = int(cls)
                    index_groups.setdefault(cls, []).append(float(v))

        reclassed = reclass_flat.reshape(arr.shape)
        mask = reclassed != 0
        shapes_gen = features.shapes(reclassed, mask=mask, transform=transform)

        features_list = []
        for geom, val in shapes_gen:
            val_int = int(val)
            geom_shp = shape(geom)
            # Aquí también se usa index_name.lower()
            state, rng = self.combined_state.get(index_name.lower(), {}).get(val_int, ["Sin clasificación", ""])
            vals = index_groups.get(val_int, [])
            mean = round(sum(vals) / len(vals), 6) if vals else None
            features_list.append({
                "geometry": geom_shp,
                "properties": {
                    "value": val_int,
                    "IndexState": state,
                    "IndexRange": rng,
                    "IndexRangeMean": mean,
                    "IndexName": index_name.upper()
                }
            })

        if not features_list:
            return gpd.GeoDataFrame()

        gdf = gpd.GeoDataFrame.from_features(features_list, crs=crs)
        dissolved = gdf.dissolve(by="value", as_index=False).to_crs(epsg=4326)
        return dissolved