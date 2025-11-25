from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import geopandas as gpd
import numpy as np
import rasterio

class IConfigurator(ABC):
    @abstractmethod
    def get_sh_config(self):
        pass

class IEvalscriptGenerator(ABC):
    @abstractmethod
    def get_evalscript(self, script_type: str, **kwargs) -> str:
        pass

class IDownloadClient(ABC):
    @abstractmethod
    def download_data(self, *args, **kwargs) -> List[str]:
        pass

class IRasterProcessor(ABC):
    @abstractmethod
    def create_mosaic(self, tiff_file_paths: List[str], output_folder: str, prefix: str) -> Tuple[np.ndarray, rasterio.transform.Affine, rasterio.crs.CRS, str]:
        pass

    @abstractmethod
    def classify_from_array(self, arr: np.ndarray, transform: rasterio.transform.Affine, crs: rasterio.crs.CRS, index_name: str) -> gpd.GeoDataFrame:
        pass

class IVectorizer(ABC):
    @abstractmethod
    def vectorize(self, raster_data_tuple: Tuple, index_name: str, output_folder: str, start_date: str = None, end_date: str = None) -> Tuple[gpd.GeoDataFrame, str]:
        pass