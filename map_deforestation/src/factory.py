from src.services.sh_config import SentinelHubConfigurator
from src.services.evalscript_gen import EvalscriptGenerator
from src.services.sh_client import SentinelHubDownloadClientWrapper
from src.services.raster_proc import RasterProcessor
from src.services.deforestation_vectorizer import DeforestationVectorizer
from src.main_service import DeforestationService

class ServiceFactory:
    @staticmethod
    def create_deforestation_service(output_folder="results"):
        configurator = SentinelHubConfigurator()
        config = configurator.get_sh_config()
        
        evalscript_gen = EvalscriptGenerator()
        download_client = SentinelHubDownloadClientWrapper(config)
        raster_proc = RasterProcessor()
        
        vectorizer = DeforestationVectorizer(raster_proc)

        return DeforestationService(
            configurator=configurator,
            evalscript_gen=evalscript_gen,
            download_client=download_client,
            raster_proc=raster_proc,
            vectorizer=vectorizer,
            output_folder=output_folder
        )