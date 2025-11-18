import sys
import os
import unittest

# --- Ensure project root is in sys.path ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.factory import ServiceFactory


class TestDownloadPolygon(unittest.TestCase):
    def setUp(self):
        """Setup executed before each test."""
        self.output_folder = "results_test"
        self.resolution = 30
        self.service = ServiceFactory.create_download_polygon_service(
            output_folder=self.output_folder,
            resolution=self.resolution
        )
        self.aoi_path = os.path.join("data", "aoi.geojson")
        self.start_date = "2024-01-01"
        self.end_date = "2024-01-02"
        self.index_name = "NDVI"
        self.threshold = 0.3

    def test_smoke(self):
        """Smoke test: ensures that the full pipeline executes successfully."""
        if not os.path.exists(self.aoi_path):
            print("⚠️ Missing AOI file at 'data/aoi.geojson'. Please add one for effective testing.")
            return

        print("\n🚀 Running smoke test for DownloadPolygonService...")

        result = self.service.process_polygons(
            self.aoi_path,
            self.start_date,
            self.end_date,
            index_name=self.index_name,
            threshold=self.threshold
        )

        # --- Assertions ---
        self.assertIsNotNone(result, "Service returned None result")
        self.assertFalse(result.error, f"Service returned an error: {result.error}")
        self.assertTrue(os.path.exists(result.tiff_output_path), "TIFF file was not created")
        self.assertTrue(os.path.exists(result.shapefile_output_path), "Shapefile was not created")

        print("✅ Smoke test passed successfully.")
        print(f"🛰️ TIFF created: {result.tiff_output_path}")
        print(f"🗺️ SHP created: {result.shapefile_output_path}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
