from src.interfaces import IEvalscriptGenerator

class BurnAreaEvalscriptGenerator(IEvalscriptGenerator):
    """
    Implementación concreta para la generación de evalscripts de áreas quemadas.
    """

    def get_burn_evalscript(self, threshold: float) -> str:
        """
        Genera el evalscript para NBR con un umbral para clasificar como quemado (1) o no quemado (0).
        """
        # Nota: La lógica se mantiene fiel a la interpretación del JS original.
        # Se recomienda revisar la lógica con el cliente si el umbral NBR
        # es para identificar quemado con valores bajos.
        return f"""
        //VERSION=3
        function setup( ){{
          return{{
            input: [{{
              bands: ["B02", "B03", "B04", "B08", "B11", "B12"],
                }}],
                output: [{{
                  id: "default", bands: 1, sampleType: SampleType.FLOAT32}},
                ]
                }}
        }}
          
        function evaluatePixel(sample) {{

          let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
          let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
          let nbr = (sample.B08 - sample.B12) / (sample.B08 + sample.B12);
          
          var isBurned;

          // Si alguna de estas condiciones es verdadera, según el JS original, era un [0] (no quemado).
          // Es crucial entender esta lógica inversa del JS original.
          // Si el NBR es mayor que el umbral (o las otras condiciones se cumplen), se considera NO quemado.
          if (
            (nbr > {threshold}) || 
            (sample.B02 > 0.1) || 
            (sample.B11 < 0.1) || 
            (ndvi > 0.3) || 
            (ndwi > 0.8)
          ) {{
              isBurned = 0; // No quemado
          }} else {{
              isBurned = 1; // Quemado
          }}

        return {{ default:[isBurned] }};
        }}
        """

    def get_burn_visual_evalscript(self, threshold: float) -> str:
        """
        Genera el evalscript para la visualización de áreas quemadas (resalta en rojo).
        """
        return f"""
        //VERSION=3
        function setup() {{
          return {{
            input: [{{
              bands: ["B02", "B03", "B04", "B08", "B11", "B12"],
            }}],
            output: [
              {{ id: "default", bands: 3, sampleType: SampleType.AUTO }}
            ]
          }}
        }}

        function evaluatePixel(sample) {{
          let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
          let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
          let nbr = (sample.B08 - sample.B12) / (sample.B08 + sample.B12);

          var image;

          if (
            (nbr > {threshold}) ||
            (sample.B02 > 0.1) ||
            (sample.B11 < 0.1) ||
            (ndvi > 0.3) ||
            (ndwi > 0.8)
          ) {{
            // No quemado: muestra en color natural
            image = [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
          }} else {{
            // Quemado: resalta en rojo
            image = [1, 0, 0];
          }}
          return {{ default: image }};   
        }}
        """