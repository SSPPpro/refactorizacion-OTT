from typing import List
import os
from sentinelhub import (
    BBox,
    DataCollection,
    MimeType,
    SentinelHubDownloadClient,
    SentinelHubRequest,
    SHConfig,
    bbox_to_dimensions
)
from src.interfaces import IDownloadClient

class SentinelHubDownloadClientWrapper(IDownloadClient):
    def __init__(self, sh_config: SHConfig):
        self._sh_config = sh_config

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
        
        sh_requests = []
        for bbox in bbox_list:
            size = bbox_to_dimensions(bbox, resolution)

            # Para análisis multitemporal con evalscript personalizado (Orbit)
            # no definimos mosaicking_order aquí, lo maneja el script internamente.
            request = SentinelHubRequest(
                evalscript=evalscript,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=data_collection,
                        time_interval=(start_date, end_date)
                    )
                ],
                responses=[SentinelHubRequest.output_response("default", mime_type)],
                bbox=bbox,
                size=size,
                data_folder=output_folder,
                config=self._sh_config,
            )
            sh_requests.append(request)

        # Descarga
        dl_requests = [req.download_list[0] for req in sh_requests]
        SentinelHubDownloadClient(config=self._sh_config).download(dl_requests, max_threads=5)

        # Recolección de archivos
        downloaded_files = []
        for root, _, files in os.walk(output_folder):
            for file in files:
                if file.lower().endswith((".tif", ".tiff")):
                    downloaded_files.append(os.path.join(root, file))

        if not downloaded_files:
            raise FileNotFoundError("No se encontraron archivos descargados.")

        return downloaded_files