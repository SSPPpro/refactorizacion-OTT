from sentinelhub import SHConfig
from dotenv import load_dotenv
import os
from src.services.sentinel_service import SentinelService
from src.services.burn_area_service import BurnAreaService
from src.services.file_service import FileService
from src.burn_zone_processor import BurnZoneProcessor

load_dotenv()  # ✅ lee el .env en la raíz del proyecto

class BurnProcessorFactory:
    @staticmethod
    def create_basic_processor(config: SHConfig = None, resolution: int = 30, threshold: float = 0.15, output_folder: str = "results"):
        # 🧩 Carga configuración de Sentinel Hub
        if config is None:
            config = SHConfig()
            config.sh_client_id = os.getenv("SH_CLIENT_ID")
            config.sh_client_secret = os.getenv("SH_CLIENT_SECRET")

            if not config.sh_client_id or not config.sh_client_secret:
                raise ValueError(
                    "⚠️ Faltan credenciales en .env. "
                    "Verifica que SH_CLIENT_ID y SH_CLIENT_SECRET estén definidos correctamente."
                )

        # 🛰️ Instanciar servicios
        sentinel = SentinelService(config=config, resolution=resolution, threshold=threshold, output_folder=output_folder)
        burn = BurnAreaService()
        file = FileService()

        # 🔥 Retornar el procesador principal
        return BurnZoneProcessor(sentinel, burn, file)
