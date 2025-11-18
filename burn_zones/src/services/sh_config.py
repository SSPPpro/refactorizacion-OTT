import os
from dotenv import load_dotenv
from sentinelhub import SHConfig

from src.interfaces import IConfigurator
from src.models import SentinelHubConfig as CustomSHConfig

class SentinelHubConfigurator(IConfigurator):
    """
    Implementación concreta para la configuración de Sentinel Hub.
    Carga credenciales desde variables de entorno.
    """
    def __init__(self):
        load_dotenv()
        self._client_id = os.getenv("SH_CLIENT_ID")
        self._client_secret = os.getenv("SH_CLIENT_SECRET")
        if not self._client_id or not self._client_secret:
            raise ValueError("Las credenciales de Sentinel Hub (SH_CLIENT_ID, SH_CLIENT_SECRET) no están configuradas en .env")

    def get_sh_config(self) -> SHConfig:
        config = SHConfig()
        config.sh_client_id = self._client_id
        config.sh_client_secret = self._client_secret
        return config