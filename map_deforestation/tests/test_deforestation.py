import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.factory import ServiceFactory

class TestDeforestationAnalysis(unittest.TestCase):
    def setUp(self):
        self.service = ServiceFactory.create_deforestation_service(output_folder="results_test")
        self.aoi_path = os.path.join("data", "aoi.geojson")
        
    def test_pipeline(self):
        if not os.path.exists(self.aoi_path):
            print("⚠️ Skipping test: AOI file not found.")
            return

        print("\n🧪 Testing Deforestation Pipeline...")
        # Usa fechas donde sepas que hay datos Sentinel-2
        result = self.service.process_deforestation(
            self.aoi_path,
            start_date="2023-01-01",
            end_date="2023-06-30"
        )

        self.assertIsNone(result.error)
        self.assertIsNotNone(result.tiff_output_path)
        print(f"Test Completed.")

if __name__ == "__main__":
    unittest.main()