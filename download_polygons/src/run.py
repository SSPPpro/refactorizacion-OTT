from src.factory import ServiceFactory
import os

if __name__ == "__main__":
    print(" Running download_polygons pipeline...")

    # Get project root (folder that contains 'src' and 'data')
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_dir = os.path.dirname(base_dir)

    # AOI path
    aoi_geojson_path = os.path.join(project_root_dir, "data", "aoi.geojson")

    # Parameters
    start_date = "2025-09-27"
    end_date = "2025-09-28"
    threshold = 0.3
    index_to_process = "NDVI"

    if not os.path.exists(aoi_geojson_path):
        print(f" AOI file not found at: {aoi_geojson_path}")
    else:
        service = ServiceFactory.create_download_polygon_service()

        result = service.process_polygons(
            aoi_geojson_path,
            start_date,
            end_date,
            index_name=index_to_process,
            threshold=threshold
        )

        if result.error:
            print(f" Error: {result.error}")
        else:
            print(f" Process completed successfully.")
            print(f" {len(result.polygons_gdf)} polygons generated.")
            print(f" Shapefile saved in: {result.shapefile_output_path}")
            print(f" Raster saved in: {result.tiff_output_path}")
