from dataclasses import dataclass
from typing import Optional

@dataclass
class Area:
    """Modelo que representa el AOI (simple)"""
    name: str
    bbox: list  # [minx, miny, maxx, maxy]
    crs: str = "EPSG:4326"

@dataclass
class BurnResult:
    """Resultado del procesamiento"""
    area_name: str
    burned_geojson: Optional[str] = None
    image_count: int = 0
    success: bool = False
    error: Optional[str] = None
