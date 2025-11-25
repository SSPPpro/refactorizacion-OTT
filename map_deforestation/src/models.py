from dataclasses import dataclass, field
from typing import Optional
import geopandas as gpd

@dataclass
class DeforestationResult:
    polygons_gdf: gpd.GeoDataFrame = field(default_factory=gpd.GeoDataFrame)
    start_date: str = ""
    end_date: str = ""
    tiff_output_path: Optional[str] = None
    shapefile_output_path: Optional[str] = None
    error: Optional[str] = None

@dataclass
class SentinelHubConfig:
    client_id: str
    client_secret: str
    base_url: str = "https://services.sentinel-hub.com"