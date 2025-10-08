import os
from src.models import Area, BurnResult
from src.utils.logger import log_process
from typing import Dict

class BurnZoneProcessor:
    """
    Orquesta el flujo: Sentinel -> detectar quemas -> guardar geojson -> metadata
    """

    def __init__(self, sentinel_service, burn_service, file_service):
        self._sentinel_service = sentinel_service
        self._burn_service = burn_service
        self._file_service = file_service

    @log_process
    def process_area(self, area: Area, date_range: Dict[str, str], output_folder: str) -> BurnResult:
        os.makedirs(output_folder, exist_ok=True)
        try:
            tiffs = self._sentinel_service.fetch_tiles(area, date_range, output_folder)
            if not tiffs:
                return BurnResult(area_name=area.name, burned_geojson=None, image_count=0, success=False, error="No se descargaron tiffs")

            out_geojson = os.path.join(output_folder, f"{area.name}_burn_areas.geojson")
            geojson_path = self._burn_service.tiffs_to_geojson(tiffs, out_geojson)

            metadata = {
                "area": area.name,
                "bbox": area.bbox,
                "image_count": len(tiffs),
                "geojson": geojson_path
            }
            meta_path = os.path.join(output_folder, f"{area.name}_metadata.json")
            self._file_service.save_metadata(metadata, meta_path)

            return BurnResult(area_name=area.name, burned_geojson=geojson_path, image_count=len(tiffs), success=True)
        except Exception as e:
            return BurnResult(area_name=area.name, burned_geojson=None, image_count=0, success=False, error=str(e))
