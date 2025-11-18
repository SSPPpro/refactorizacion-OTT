from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import geopandas as gpd
from sentinelhub import SHConfig, BBox, MimeType, DataCollection

# Modelos
from src.models import SentinelHubConfig as CustomSHConfig, BurnAnalysisResult

class IConfigurator(ABC):
    """Interfaz para la configuración de Sentinel Hub."""
    @abstractmethod
    def get_sh_config(self) -> SHConfig:
        pass

class IEvalscriptGenerator(ABC):
    """Interfaz para la generación de evalscripts."""
    @abstractmethod
    def get_burn_evalscript(self, threshold: float) -> str:
        pass

    @abstractmethod
    def get_burn_visual_evalscript(self, threshold: float) -> str:
        pass

class IDownloadClient(ABC):
    """Interfaz para la descarga de datos de Sentinel Hub."""
    @abstractmethod
    def download_data(
        self,
        bbox_list: List[BBox],
        evalscript: str,
        start_date: str,
        end_date: str,
        output_folder: str,
        resolution: int,
        mime_type: MimeType = MimeType.TIFF,
        data_collection: DataCollection = DataCollection.SENTINEL2_L2A
    ) -> List[str]:
        pass

class IRasterProcessor(ABC):
    """Interfaz para operaciones con ráster (e.g., mosaico)."""
    @abstractmethod
    def create_mosaic(self, tiff_file_paths: List[str], output_path: str) -> Optional[str]:
        pass

class IVectorizer(ABC):
    """Interfaz para la vectorización de datos ráster."""
    @abstractmethod
    def vectorize_burn_areas(self, burn_area_tif_path: str) -> gpd.GeoDataFrame:
        pass

class IBurnAreaService(ABC):
    """Interfaz principal para el servicio de análisis de áreas quemadas."""
    @abstractmethod
    def analyze_burn_areas(self, aoi_geojson_path: str, start_date: str, end_date: str, burn_threshold: float) -> BurnAnalysisResult:
        pass