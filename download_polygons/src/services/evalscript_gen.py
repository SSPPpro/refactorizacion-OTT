from src.interfaces import IEvalscriptGenerator

class EvalscriptGenerator(IEvalscriptGenerator): # Aseguramos que implementa la interfaz
    """
    Evalscript provider: devuelve el evalscript por nombre de índice.
    Basado en los scripts JS originales (NDVI, GNDVI, EVI, SAVI, NDMI, NDSI, NDWI, NDBI, NDCI, NBR).
    """
    SCRIPTS = {
        "NDVI": """//VERSION=3
function setup() {
  return { input:[{bands:["B04","B08"], units:"REFLECTANCE"}], output:{id:"default",bands:1,sampleType:SampleType.FLOAT32} };
}
function evaluatePixel(sample){ return [(sample.B08 - sample.B04)/(sample.B08 + sample.B04)]; }
""",
        "GNDVI": """//VERSION=3
function setup(){ return { input:[{bands:["B03","B08"], units:"REFLECTANCE"}], output:{id:"default",bands:1,sampleType:SampleType.FLOAT32} }; }
function evaluatePixel(sample){ return [(sample.B08 - sample.B03)/(sample.B08 + sample.B03)]; }
""",
        "EVI": """//VERSION=3
function setup(){ return { input:[{bands:["B02","B04","B08","dataMask"], units:"REFLECTANCE"}], output:{id:"default",bands:1,sampleType:SampleType.FLOAT32} }; }
function evaluatePixel(sample){ if(sample.dataMask === 0) return [NaN]; return [2.5*((sample.B08 - sample.B04)/(sample.B08 + 6*sample.B04 - 7.5*sample.B02 + 1))]; }
""",
        "SAVI": """//VERSION=3
function setup(){ return { input:[{bands:["B04","B08","dataMask"], units:"REFLECTANCE"}], output:{id:"default",bands:1,sampleType:SampleType.FLOAT32} }; }
function evaluatePixel(sample){ if(sample.dataMask === 0) return [NaN]; let L=0.428; return [((sample.B08 - sample.B04)/(sample.B08 + sample.B04 + L))*(1.0 + L)]; }
""",
        "NDMI": """//VERSION=3
function setup(){ return { input:[{bands:["B08","B11"], units:"REFLECTANCE"}], output:{id:"default",bands:1,sampleType:SampleType.FLOAT32} }; }
function evaluatePixel(sample){ return [(sample.B08 - sample.B11)/(sample.B08 + sample.B11)]; }
""",
        "NDSI": """//VERSION=3
function setup(){ return { input:[{bands:["B03","B11"], units:"REFLECTANCE"}], output:{id:"default",bands:1,sampleType:SampleType.FLOAT32} }; }
function evaluatePixel(sample){ return [(sample.B03 - sample.B11)/(sample.B03 + sample.B11)]; }
""",
        "NDWI": """//VERSION=3
function setup(){ return { input:[{bands:["B03","B08"], units:"REFLECTANCE"}], output:{id:"default",bands:1,sampleType:SampleType.FLOAT32} }; }
function evaluatePixel(sample){ return [(sample.B03 - sample.B08)/(sample.B03 + sample.B08)]; }
""",
        "NDBI": """//VERSION=3
function setup(){ return { input:[{bands:["B08","B11"], units:"REFLECTANCE"}], output:{id:"default",bands:1,sampleType:SampleType.FLOAT32} }; }
function evaluatePixel(sample){ return [(sample.B11 - sample.B08)/(sample.B08 + sample.B11)]; }
""",
        "NDCI": """//VERSION=3
function setup(){ return { input:[{bands:["B05","B04"], units:"REFLECTANCE"}], output:{id:"default",bands:1,sampleType:SampleType.FLOAT32} }; }
function evaluatePixel(sample){ return [(sample.B05 - sample.B04)/(sample.B05 + sample.B04)]; }
""",
        "NBR": """//VERSION=3
function setup(){ return { input:[{bands:["B08","B12"], units:"REFLECTANCE"}], output:{id:"default",bands:1,sampleType:SampleType.FLOAT32} }; }
function evaluatePixel(sample){ return [(sample.B08 - sample.B12)/(sample.B08 + sample.B12)]; }
"""
    }

    def get_evalscript(self, index_name: str) -> str:
        """Devuelve el evalscript JS para el índice especificado."""
        if not isinstance(index_name, str):
            print(f"ADVERTENCIA: 'index_name' en get_evalscript debe ser una cadena, se recibió {type(index_name).__name__}.")
            # Lanza un TypeError para detener la ejecución y hacer el problema evidente.
            raise TypeError(f"El argumento 'index_name' en get_evalscript debe ser una cadena, pero se recibió un {type(index_name).__name__}.")
        
        # Siempre capitalizar para que coincida con las claves del diccionario
        # Esto es lo que hicimos antes, pero es bueno revisar.
        evalscript = self.SCRIPTS.get(index_name.upper())
        
        if evalscript is None:
            print(f"ADVERTENCIA: No se encontró evalscript para el índice '{index_name.upper()}'.")
        
        return evalscript