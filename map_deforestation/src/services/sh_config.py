import os
from dotenv import load_dotenv
from sentinelhub import SHConfig
from src.interfaces import IConfigurator

class SentinelHubConfigurator(IConfigurator):
    def __init__(self):
        load_dotenv()
        self._client_id = os.getenv("SH_CLIENT_ID")
        self._client_secret = os.getenv("SH_CLIENT_SECRET")

        if not self._client_id or not self._client_secret:
            raise ValueError("Sentinel Hub credentials not found in .env")

    def get_sh_config(self) -> SHConfig:
        config = SHConfig()
        config.sh_client_id = self._client_id
        config.sh_client_secret = self._client_secret
        return config