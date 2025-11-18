import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Importar la Factory correcta
from src.factory import BurnAreaServiceFactory 

# Carga las variables de entorno del archivo .env
load_dotenv()

PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # La raíz del proyecto 'burn_zones'

def load_aoi_geojson_path(relative_path_to_aoi: str):
    """
    Determina la ruta completa al archivo aoi.geojson, asumiendo que está en 'data/'.
    """
    aoi_path = os.path.join(PROJECT_ROOT_DIR, relative_path_to_aoi)
    if not os.path.exists(aoi_path):
        raise FileNotFoundError(f"No se encontró el archivo AOI en: {aoi_path}")
    return aoi_path

if __name__ == "__main__":
    print(" Iniciando proceso de detección de zonas quemadas...")

    # Rutas y configuración
    aoi_relative_path = "data/aoi.geojson" # Asume aoi.geojson está en burn_zones/data/
    output_folder = os.path.join(PROJECT_ROOT_DIR, "results") # Carpeta 'results' en la raíz de burn_zones

    os.makedirs(output_folder, exist_ok=True) # Asegura que la carpeta de resultados exista

    # Cargar la ruta completa del AOI
    aoi_full_path = load_aoi_geojson_path(aoi_relative_path)

    # Intervalo de fechas (ajusta si es necesario)
    start_date_str = "2025-09-27"
    end_date_str = "2025-09-28"
    burn_threshold_val = 1 # Umbral para la detección de quemados

    # Crear el servicio usando la Factory
    # Pasamos el output_folder y resolution que son parámetros del factory
    burn_service_instance = BurnAreaServiceFactory.create_default_service(
        output_folder=output_folder,
        resolution=10 # Puedes ajustar la resolución si necesitas una más baja o alta
    )

    # Ejecutar el análisis
    result = burn_service_instance.analyze_burn_areas(
        aoi_geojson_path=aoi_full_path,
        start_date=start_date_str,
        end_date=end_date_str,
        burn_threshold=burn_threshold_val
    )

    if result.error:
        print(f" Hubo un error en el proceso: {result.error}")
    else:
        print(f" Proceso finalizado correctamente. GeoDataFrame de quemados: {len(result.burn_areas_gdf)} registros.")
        if result.visual_image_path:
            print(f" Imagen visual generada en: {result.visual_image_path}")
        else:
            print(" No se generó imagen visual.")
        
        # Opcional: imprimir el GeoJSON resultante si existe
        if not result.burn_areas_gdf.empty:
            geojson_output_path = os.path.join(output_folder, f"burnt_areas_{start_date_str}_{end_date_str}.geojson")
            print(f"GeoJSON de áreas quemadas guardado en: {geojson_output_path}")
        else:
            print("No se detectaron áreas quemadas significativas.")