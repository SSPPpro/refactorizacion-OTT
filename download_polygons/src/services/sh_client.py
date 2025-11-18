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
    """
    Implementación concreta para la descarga de datos desde Sentinel Hub.
    Envuelve SentinelHubRequest y SentinelHubDownloadClient.
    """

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
        """
        Prepara y ejecuta la descarga de datos de Sentinel Hub.
        """
        sh_requests = []
        for bbox in bbox_list:
            #  Calcular tamaño en píxeles según resolución
            size = bbox_to_dimensions(bbox, resolution)

            request = SentinelHubRequest(
                evalscript=evalscript,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=data_collection,
                        time_interval=(start_date, end_date),
                    )
                ],
                responses=[SentinelHubRequest.output_response("default", mime_type)],
                bbox=bbox,
                size=size,
                data_folder=output_folder,
                config=self._sh_config,
            )
            sh_requests.append(request)

        #  Descargar todos los requests concurrentemente
        dl_requests = [req.download_list[0] for req in sh_requests]
        SentinelHubDownloadClient(config=self._sh_config).download(dl_requests, max_threads=5)

        #  Buscar los archivos descargados en el directorio destino
        downloaded_files = []
        for root, _, files in os.walk(output_folder):
            for file in files:
                if file.lower().endswith((".tif", ".tiff", ".png")):
                    downloaded_files.append(os.path.join(root, file))

        if not downloaded_files:
            raise FileNotFoundError("No se encontraron archivos descargados en la carpeta de salida.")

        return downloaded_files
