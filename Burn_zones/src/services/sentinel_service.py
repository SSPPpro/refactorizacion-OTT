import os
import glob
from typing import List, Dict
from sentinelhub import (
    SHConfig,
    SentinelHubRequest,
    SentinelHubDownloadClient,
    DataCollection,
    MimeType,
    bbox_to_dimensions,
    BBox,
    CRS
)
from src.interfaces import ISentinelService

class SentinelService(ISentinelService):
    """
    Implementación que usa sentinelhub-py para crear la request y descargar TIFFs.
    Requiere que tengas SH_CLIENT_ID y SH_CLIENT_SECRET en .env (o en tu entorno).
    """

    def __init__(self, config: SHConfig = None, resolution: int = 10, threshold: float = 0.15, output_folder: str = "results"):
        self.config = config or SHConfig()
        self.resolution = resolution
        self.threshold = threshold
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

    def _get_evalscript(self) -> str:
        return f"""
        //VERSION=3
        function setup() {{
            return {{
                input: ["B08","B12"],
                output: {{
                    bands: 1,
                    sampleType: "UINT8"
                }}
            }};
        }}
        function evaluatePixel(sample) {{
            let nbr = (sample.B08 - sample.B12) / (sample.B08 + sample.B12);
            return [nbr > {self.threshold} ? 1 : 0];
        }}
        """

    def fetch_tiles(self, area, date_range: Dict[str, str], output_folder: str) -> List[str]:
        """Crea request para la bbox del area y descarga TIFFs en output_folder"""
        bbox = BBox(bbox=area.bbox, crs=CRS.WGS84)
        size = bbox_to_dimensions(bbox, resolution=self.resolution)
        evalscript = self._get_evalscript()

        request = SentinelHubRequest(
            evalscript=evalscript,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=(date_range["from"], date_range["to"])
                )
            ],
            responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
            bbox=bbox,
            size=size,
            data_folder=output_folder,
            config=self.config
        )

        # prepare download list and download
        dl_list = [request.download_list[0]]
        client = SentinelHubDownloadClient(config=self.config)
        client.download(dl_list, max_threads=5)

        # buscar tiffs en la carpeta
        tiffs = []
        for root, _, files in os.walk(output_folder):
            for f in files:
                if f.lower().endswith((".tif", ".tiff")):
                    tiffs.append(os.path.join(root, f))
        return sorted(set(tiffs))
