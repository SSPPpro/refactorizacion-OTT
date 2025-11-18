from typing import List, Optional
import os
import rasterio as rio
from rasterio.merge import merge

from src.interfaces import IRasterProcessor

class RasterProcessor(IRasterProcessor):
    """
    Implementación concreta para el procesamiento de ráster.
    Actualmente solo soporta la creación de mosaicos TIFF.
    """

    def create_mosaic(self, tiff_file_paths: List[str], output_path: str) -> Optional[str]:
        """
        Crea un mosaico a partir de una lista de archivos TIFF.
        """
        if not tiff_file_paths:
            print("No hay archivos TIFF para crear el mosaico.")
            return None

        src_files_to_mosaic = []
        for fp in tiff_file_paths:
            try:
                src_files_to_mosaic.append(rio.open(fp))
            except Exception as e:
                print(f"Error abriendo archivo {fp}: {e}")
                
        if not src_files_to_mosaic:
            print("No se pudieron abrir archivos TIFF válidos para el mosaico.")
            return None

        # Si solo hay un archivo, no es necesario hacer un mosaico, simplemente retornamos la ruta.
        if len(src_files_to_mosaic) == 1:
            single_file_path = src_files_to_mosaic[0].name
            src_files_to_mosaic[0].close()
            return single_file_path

        try:
            mosaic, out_trans = merge(src_files_to_mosaic)
            
            out_meta = src_files_to_mosaic[0].meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": mosaic.shape[1],
                "width": mosaic.shape[2],
                "transform": out_trans,
                "crs": src_files_to_mosaic[0].crs
            })

            with rio.open(output_path, "w", **out_meta) as dest:
                dest.write(mosaic)
            
            print(f"Mosaico creado en: {output_path}")
            return output_path

        except Exception as e:
            print(f"Error creando mosaico: {e}")
            return None
        finally:
            for src in src_files_to_mosaic:
                src.close()