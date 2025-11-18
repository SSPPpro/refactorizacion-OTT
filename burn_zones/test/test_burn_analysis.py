import os
import sys
import folium
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import geopandas as gpd
from shapely.geometry import shape
from sentinelhub import read_data

from src.factory import BurnAreaServiceFactory
from src.models import BurnAnalysisResult



def run_burn_analysis():
    """
    Función principal para configurar y ejecutar el análisis de áreas quemadas.
    """
    # 1. Configuración de parámetros de entrada
    input_aoi_path = "data/aoi.geojson" 
    start_date_analysis = "2025-09-27"
    end_date_analysis = "2025-09-28"
    burn_detection_threshold = 0.2  # Umbral para NBR

    # Validar que el archivo AOI exista
    if not os.path.exists(input_aoi_path):
        print(f"Error: El archivo AOI no se encontró en '{input_aoi_path}'")
        print("Por favor, asegúrate de tener 'aoi_3.json' dentro de la carpeta 'geometry/'.")
        return

    # 2. Crear el servicio de análisis usando la fábrica
    # Esto inyecta todas las dependencias necesarias.
    try:
        burn_service = BurnAreaServiceFactory.create_default_service()
    except ValueError as e:
        print(f"Error de configuración de Sentinel Hub: {e}")
        print("Asegúrate de que SH_CLIENT_ID y SH_CLIENT_SECRET estén en tu archivo .env.")
        return

    # 3. Ejecutar el análisis
    print("Iniciando la ejecución del servicio de análisis de quemados...")
    result: BurnAnalysisResult = burn_service.analyze_burn_areas(
        aoi_geojson_path=input_aoi_path,
        start_date=start_date_analysis,
        end_date=end_date_analysis,
        burn_threshold=burn_detection_threshold
    )

    # 4. Mostrar resultados
    print("\n--- Resultados del Análisis ---")
    if result.error:
        print(f"Se produjo un error durante el análisis: {result.error}")

# 🔹 Punto de entrada del script
if __name__ == "__main__":
    run_burn_analysis()