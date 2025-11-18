from abc import ABC, abstractmethod
from typing import List, Tuple, Any
import geopandas as gpd
import numpy as np
import rasterio

class IConfigurator(ABC):
    @abstractmethod
    def get_sh_config(self):
        pass


class IEvalscriptGenerator(ABC):
    @abstractmethod
    def get_evalscript(self, index_name: str) -> str:
        pass


class IDownloadClient(ABC):
    @abstractmethod
    def download_data(self, *args, **kwargs) -> List[str]:
        pass


class IRasterProcessor(ABC):
    # Devuelve también la ruta del TIFF guardado
    @abstractmethod
    def create_mosaic(self, tiff_file_paths: List[str], output_folder: str, index_name: str) -> Tuple[np.ndarray, rasterio.transform.Affine, rasterio.crs.CRS, str]:
        pass

    @abstractmethod
    def classify_from_array(self, arr: np.ndarray, transform: rasterio.transform.Affine, crs: rasterio.crs.CRS, index_name: str) -> gpd.GeoDataFrame:
        pass


class IVectorizer(ABC):
    # Devuelve también la ruta del shapefile guardado
    @abstractmethod
    def vectorize(self, raster_data_tuple: Tuple[np.ndarray, rasterio.transform.Affine, rasterio.crs.CRS], index_name: str, output_folder: str, threshold: float = None) -> Tuple[gpd.GeoDataFrame, str]:
        pass


class IDownloadPolygonService(ABC):
    @abstractmethod
    def process_polygons(self, aoi_geojson_path: str, start_date: str, end_date: str, index_name: str, threshold: float) -> Any:
        pass