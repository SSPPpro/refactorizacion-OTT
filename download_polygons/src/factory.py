from src.services.sh_config import SentinelHubConfigurator
from src.services.evalscript_gen import EvalscriptGenerator
from src.services.sh_client import SentinelHubDownloadClientWrapper
from src.services.raster_proc import RasterProcessor
from src.main_service import DownloadPolygonService


class ServiceFactory:
    @staticmethod
    def create_download_polygon_service(output_folder="results", resolution=10):
        configurator = SentinelHubConfigurator()
        config = configurator.get_sh_config()
        evalscript_generator = EvalscriptGenerator()
        download_client = SentinelHubDownloadClientWrapper(config)
        raster_processor = RasterProcessor()  # sin argumentos adicionales

        service = DownloadPolygonService(
            configurator=configurator,
            evalscript_generator=evalscript_generator,
            download_client=download_client,
            raster_processor=raster_processor,
            output_folder=output_folder,
            resolution=resolution
        )

        return service
