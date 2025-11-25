from src.factory import ServiceFactory
import os

if __name__ == "__main__":
    print(" Running Deforestation Detection")

    # Get project root
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_dir = os.path.dirname(base_dir)

    # Rutas y Parámetros
    aoi_geojson_path = os.path.join(project_root_dir, "data", "aoi.geojson")
    
    # Rango de fechas: Sentinel necesita un rango amplio para comparar "antes" y "ahora"
    # Asegúrate de que este rango cubra las imágenes que quieres comparar
    start_date = "2025-07-01" 
    end_date = "2025-09-30" 
    
    threshold = 0.1 

    if not os.path.exists(aoi_geojson_path):
        print(f" AOI file not found at: {aoi_geojson_path}")
    else:
        service = ServiceFactory.create_deforestation_service()

        result = service.process_deforestation(
            aoi_geojson_path,
            start_date,
            end_date,
            threshold=threshold
        )

        if result.error:
            print(f" Error: {result.error}")
        else:
            print(f" Process completed successfully.")
            if not result.polygons_gdf.empty:
                print(f" {len(result.polygons_gdf)} deforestation polygons detected.")
                print(f" Shapefile saved in: {result.shapefile_output_path}")
                print(f" Raster saved in: {result.tiff_output_path}")
            else:
                print(" No deforestation detected with current parameters.")