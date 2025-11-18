from dataclasses import dataclass, field
from typing import Optional
import geopandas as gpd

@dataclass
class DownloadPolygonResult:
    polygons_gdf: gpd.GeoDataFrame = field(default_factory=gpd.GeoDataFrame)
    start_date: str = ""
    end_date: str = ""
    aoi_geojson_path: str = ""
    tiff_output_path: Optional[str] = None  # Nuevo: Ruta al archivo TIFF del índice
    shapefile_output_path: Optional[str] = None  # Nuevo: Ruta al archivo Shapefile
    error: Optional[str] = None

@dataclass
class SentinelHubConfig:
    client_id: str
    client_secret: str
    base_url: str = "https://services.sentinel-hub.com"