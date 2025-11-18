from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import geopandas as gpd

@dataclass
class BurnAnalysisResult:
    """
    Modelo para los resultados del análisis de áreas quemadas.
    Contiene el GeoDataFrame de las zonas quemadas y opcionalmente
    información sobre el archivo de imagen visual.
    """
    burn_areas_gdf: gpd.GeoDataFrame = field(default_factory=gpd.GeoDataFrame)
    visual_image_path: Optional[str] = None
    error: Optional[str] = None
    start_date: str = ""
    end_date: str = ""
    aoi_geojson_path: str = ""

@dataclass
class SentinelHubConfig:
    """
    Modelo para la configuración de Sentinel Hub.
    """
    client_id: str
    client_secret: str
    base_url: str = "https://services.sentinel-hub.com"