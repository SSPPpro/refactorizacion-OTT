import os
import json
from datetime import datetime
from src.factory import BurnProcessorFactory
from src.models import Area

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_aoi_bounds(aoi_path: str):
    """Carga AOI GeoJSON y devuelve bbox [minx, miny, maxx, maxy]"""
    with open(aoi_path, "r", encoding="utf-8") as f:
        gj = json.load(f)
    geom = gj["features"][0]["geometry"]
    coords = geom.get("coordinates")[0]
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    return [min(xs), min(ys), max(xs), max(ys)]

if __name__ == "__main__":
    print("🚀 Iniciando proceso de detección de zonas quemadas...")

    # 📂 Carpeta donde están los AOI ("data/")
    aoi_dir = os.path.join(PROJECT_DIR, "data")
    if not os.path.exists(aoi_dir):
        raise FileNotFoundError(f"No existe la carpeta {aoi_dir}. Crea una carpeta llamada 'data' y coloca tus AOI GeoJSON allí.")

    # 📂 Carpeta de salida
    output_folder = os.path.join(PROJECT_DIR, "results")
    os.makedirs(output_folder, exist_ok=True)

    # 📅 Fechas del intervalo
    date_from = "2024-01-10T00:00:00Z"
    date_to = "2024-01-23T23:59:59Z"
    date_range = {"from": date_from, "to": date_to}

    # ⚙️ Crear el procesador
    processor = BurnProcessorFactory.create_basic_processor(
        resolution=30,
        threshold=0.15,
        output_folder=output_folder
    )

    # 🔁 Procesar cada AOI dentro de /data
    for filename in os.listdir(aoi_dir):
        if filename.endswith(".geojson"):
            aoi_path = os.path.join(aoi_dir, filename)
            print(f"\n📍 Procesando AOI: {filename}")

            try:
                bbox = load_aoi_bounds(aoi_path)
                area_name = os.path.splitext(filename)[0]
                area = Area(name=area_name, bbox=bbox)

                result = processor.process_area(area, date_range, output_folder)

                if result.success:
                    print(f"✅ Archivo generado: {result.burned_geojson}")
                else:
                    print(f"❌ Error en {filename}: {result.error}")

            except Exception as e:
                print(f"⚠️ No se pudo procesar {filename}: {e}")

    print("\n🎯 Proceso finalizado correctamente.")
