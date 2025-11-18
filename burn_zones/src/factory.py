from src.interfaces import IBurnAreaService
from src.services.sh_config import SentinelHubConfigurator
from src.services.evalscript_gen import BurnAreaEvalscriptGenerator
from src.services.sh_client import SentinelHubDownloadClientWrapper
from src.services.raster_proc import RasterProcessor
from src.services.burn_vectorizer import BurnAreaVectorizer
from src.main_service import BurnAreaService

class BurnAreaServiceFactory:
    """
    Factory para crear instancias configuradas de BurnAreaService.
    """

    @staticmethod
    def create_default_service(output_folder: str = "results", resolution: int = 10) -> IBurnAreaService:
        """
        Crea una instancia preconfigurada de BurnAreaService con las implementaciones por defecto.
        """
        configurator = SentinelHubConfigurator()
        evalscript_generator = BurnAreaEvalscriptGenerator()
        download_client = SentinelHubDownloadClientWrapper(sh_config=configurator.get_sh_config())
        raster_processor = RasterProcessor()
        vectorizer = BurnAreaVectorizer()

        return BurnAreaService(
            configurator=configurator,
            evalscript_generator=evalscript_generator,
            download_client=download_client,
            raster_processor=raster_processor,
            vectorizer=vectorizer,
            output_folder=output_folder,
            resolution=resolution
        )