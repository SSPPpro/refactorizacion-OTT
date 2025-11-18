import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from sentinelhub import BBox, CRS, MimeType
from src.services.sh_config import SentinelHubConfigurator
from src.services.evalscript_gen import BurnAreaEvalscriptGenerator
from src.services.sh_client import SentinelHubDownloadClient
from src.services.raster_proc import RasterProcessor
from src.services.burn_vectorizer import BurnAreaVectorizer
from src.interfaces import IBurnAreaService
from src.models import BurnAnalysisResult


class BurnAreaService(IBurnAreaService):
    def __init__(
        self,
        configurator=SentinelHubConfigurator(),
        evalscript_generator=BurnAreaEvalscriptGenerator(),
        download_client=SentinelHubDownloadClient(),
        raster_processor=RasterProcessor(),
        vectorizer=BurnAreaVectorizer(),
        output_folder: str = "results",
        resolution: int = 10,
    ):
        self._sh_config = configurator.get_sh_config()
        self._evalscript_gen = evalscript_generator
        self._download_client = download_client
        self._raster_processor = raster_processor
        self._vectorizer = vectorizer
        self._output_folder = output_folder
        self._resolution = resolution

        # Crear estructura
        os.makedirs(self._output_folder, exist_ok=True)
        raster_folder = os.path.join(self._output_folder, "raster")
        vector_folder = os.path.join(self._output_folder, "vector")

        # 🔹 Solo limpiar los archivos del raster, no del vector
        if os.path.exists(raster_folder):
            for f in os.listdir(raster_folder):
                os.remove(os.path.join(raster_folder, f))
        else:
            os.makedirs(raster_folder, exist_ok=True)

        os.makedirs(vector_folder, exist_ok=True)

    def analyze_burn_areas(
        self, aoi_geojson_path: str, start_date: str, end_date: str, burn_threshold: float
    ) -> BurnAnalysisResult:
        try:
            print(f" Iniciando análisis de áreas quemadas ({start_date} a {end_date})")

            # 1️ Cargar AOI
            with open(aoi_geojson_path, "r", encoding="utf-8") as f:
                geojson_data = json.load(f)

            coords = geojson_data["features"][0]["geometry"]["coordinates"][0]
            lons, lats = [c[0] for c in coords], [c[1] for c in coords]
            aoi_bbox = BBox([min(lons), min(lats), max(lons), max(lats)], crs=CRS.WGS84)
            bbox_list = [aoi_bbox]

            # 2️ Evalscript NBR
            evalscript_burn = self._evalscript_gen.get_burn_evalscript(threshold=burn_threshold)

            # 3️ Descargar TIFF
            print(" Descargando ráster binario...")
            raster_folder = os.path.join(self._output_folder, "raster")
            downloaded_burn_files = self._download_client.download_data(
                bbox_list=bbox_list,
                evalscript=evalscript_burn,
                start_date=start_date,
                end_date=end_date,
                output_folder=raster_folder,
                resolution=self._resolution,
                mime_type=MimeType.TIFF,
            )

            if not downloaded_burn_files:
                print(" No se encontraron imágenes NBR.")
                return BurnAnalysisResult(error="No se encontraron imágenes NBR.")

            burn_mosaic_path = os.path.join(raster_folder, f"burn_mosaic_{start_date}_{end_date}.tif")
            burn_mosaic_path = self._raster_processor.create_mosaic(downloaded_burn_files, burn_mosaic_path)

            # 4️ Vectorizar áreas quemadas
            print("🧩 Vectorizando áreas quemadas...")
            burn_gdf = self._vectorizer.vectorize_burn_areas(
                burn_mosaic_path, start_date=start_date, end_date=end_date
            )

            # 5️ Imagen visual (PNG)
            print(" Descargando visualización PNG...")
            evalscript_visual = self._evalscript_gen.get_burn_visual_evalscript(threshold=burn_threshold)
            self._download_client.download_data(
                bbox_list=bbox_list,
                evalscript=evalscript_visual,
                start_date=start_date,
                end_date=end_date,
                output_folder=raster_folder,
                resolution=self._resolution,
                mime_type=MimeType.PNG,
            )

            # 6️ Guardar resumen
            response_path = os.path.join(self._output_folder, "response.json")
            result_data = {
                "start_date": start_date,
                "end_date": end_date,
                "tif_path": burn_mosaic_path,
                "visual_png": os.path.join(raster_folder, "visual_image.png"),
                "vector_shp": os.path.join(self._output_folder, "vector", "burn_areas_with_fields.shp"),
                "vector_geojson": os.path.join(self._output_folder, f"burnt_areas_{start_date}_{end_date}.geojson"),
            }

            with open(response_path, "w", encoding="utf-8") as f:
                json.dump(result_data, f, indent=4)

            print(f" Resumen guardado en: {response_path}")

            return BurnAnalysisResult(
                burn_areas_gdf=burn_gdf,
                visual_image_path=result_data["visual_png"],
                start_date=start_date,
                end_date=end_date,
                aoi_geojson_path=aoi_geojson_path,
            )

        except Exception as e:
            print(f" Error en el análisis: {e}")
            return BurnAnalysisResult(error=str(e))
