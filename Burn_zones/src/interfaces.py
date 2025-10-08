from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ISentinelService(ABC):
    @abstractmethod
    def fetch_tiles(self, area, date_range: Dict[str, str], output_folder: str) -> List[str]:
        """Descarga/obtiene tiff(s) y devuelve lista de rutas a los TIFFs locales"""
        raise NotImplementedError

class IBurnAreaService(ABC):
    @abstractmethod
    def tiffs_to_geojson(self, tiff_paths: List[str], out_geojson: str) -> str:
        """Convierte TIFFs en un GeoJSON de áreas quemadas"""
        raise NotImplementedError

class IFileService(ABC):
    @abstractmethod
    def save_metadata(self, metadata: Dict[str, Any], out_path: str) -> str:
        """Guarda un JSON con metadata / resumen"""
        raise NotImplementedError
