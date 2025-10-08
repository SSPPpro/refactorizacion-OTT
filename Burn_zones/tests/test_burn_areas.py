import unittest
import tempfile
import os
import shutil
import numpy as np
import rasterio
from rasterio.transform import from_origin
from src.services.burn_area_service import BurnAreaService
from src.burn_zone_processor import BurnZoneProcessor
from src.services.file_service import FileService
from src.models import Area

class MockSentinelService:
    """Mock que simula la descarga devolviendo la ruta a un tiff ya creado."""
    def __init__(self, tiff_path):
        self.tiff_path = tiff_path

    def fetch_tiles(self, area, date_range, output_folder):
        # copiar tiff a output_folder para simular descarga
        os.makedirs(output_folder, exist_ok=True)
        dst = os.path.join(output_folder, os.path.basename(self.tiff_path))
        shutil.copy(self.tiff_path, dst)
        return [dst]

class TestBurnAreas(unittest.TestCase):
    def setUp(self):
        # carpeta temporal
        self.tmpdir = tempfile.mkdtemp()
        # crear un tiff binario pequeño con algunos pixeles = 1 (quemado)
        self.tif = os.path.join(self.tmpdir, "fake_burn.tif")
        arr = np.zeros((10, 10), dtype=np.uint8)
        arr[2:5, 3:7] = 1  # área quemada
        transform = from_origin(-76.66, 2.38, 0.001, 0.001)  # lon, lat, xres, yres
        with rasterio.open(
            self.tif, 'w',
            driver='GTiff',
            height=arr.shape[0],
            width=arr.shape[1],
            count=1,
            dtype=arr.dtype,
            crs='EPSG:4326',
            transform=transform
        ) as dst:
            dst.write(arr, 1)

        # services
        self.mock_sentinel = MockSentinelService(self.tif)
        self.burn_service = BurnAreaService()
        self.file_service = FileService()
        self.processor = BurnZoneProcessor(self.mock_sentinel, self.burn_service, self.file_service)

        self.area = Area(name="TestArea", bbox=[-76.66, 2.37, -76.65, 2.38])

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_basic_processing(self):
        out_dir = os.path.join(self.tmpdir, "out")
        result = self.processor.process_area(self.area, {"from":"2025-01-01T00:00:00Z","to":"2025-01-31T23:59:59Z"}, out_dir)
        # Assert success and files generated
        self.assertTrue(result.success)
        self.assertIsNotNone(result.burned_geojson)
        self.assertTrue(os.path.exists(result.burned_geojson))
        # metadata file
        metadata_path = os.path.join(out_dir, "TestArea_metadata.json")
        self.assertTrue(os.path.exists(metadata_path))

if __name__ == "__main__":
    unittest.main()
