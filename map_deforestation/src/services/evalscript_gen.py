from src.interfaces import IEvalscriptGenerator

class EvalscriptGenerator(IEvalscriptGenerator):
    
    def get_evalscript(self, script_type: str, **kwargs) -> str:
        if script_type.upper() == "DEFORESTATION":
            # Obtenemos el threshold de los argumentos, por defecto 0.1 si no se envía
            threshold_val = kwargs.get('threshold', 0.1)
            
            # Inyectamos el valor usando f-string en Python
            return f"""
            //VERSION=3
            
            // AQUI SE INYECTA TU VALOR DINAMICO
            const NDVI_THRESHOLD = {threshold_val}; 
            
            const NDWI_THRESHOLD = 0.5; 
            const BRIGHTNESS_THRESHOLD = 0.18; 
            const WINDOW_DAYS = 0; 
            const CLOUD_PROBABILITY_THRESHOLD = 0.3;

            function setup() {{
                return {{
                    input: [{{
                        bands: ["B02", "B03", "B04", "B08", "CLD"],
                    }}],
                    output: [{{
                        id: "default",
                        bands: 1,
                        sampleType: "UINT8"
                    }}],
                    mosaicking: "ORBIT"
                }};
            }}

            function calcIndex(x, y) {{
                return (x - y) / (x + y);
            }}

            function evaluatePixel(samples, scenes) {{
                const sortedScenes = scenes.map((s, i) => ({{ scene: s, index: i }}))
                                           .sort((a, b) => b.scene.date.getTime() - a.scene.date.getTime());
                
                if (sortedScenes.length === 0) return [0];

                const recentDate = sortedScenes[0].scene.date;
                const oldestDate = sortedScenes[sortedScenes.length - 1].scene.date;

                const recentIndices = sortedScenes.filter(
                    (item) => recentDate.getTime() - item.scene.date.getTime() <= WINDOW_DAYS * 24 * 3600 * 1000
                ).map(item => item.index);

                const oldestIndices = sortedScenes.filter(
                    (item) => item.scene.date.getTime() - oldestDate.getTime() <= WINDOW_DAYS * 24 * 3600 * 1000
                ).map(item => item.index);

                function isCloudOrWater(sample) {{
                    const brightness = sample.B02; 
                    const cloudProb = sample.CLD; 
                    const NDWI = calcIndex(sample.B03, sample.B08); 
                    
                    const isCloud = brightness > BRIGHTNESS_THRESHOLD || cloudProb > CLOUD_PROBABILITY_THRESHOLD;
                    const isWater = NDWI >= NDWI_THRESHOLD;
                    return isCloud || isWater;
                }}

                function calculateMeanNDVI(indicesArray) {{
                    let sumNDVI = 0;
                    let count = 0;
                    
                    indicesArray.forEach((idx) => {{
                        const sample = samples[idx];
                        if (sample && !isCloudOrWater(sample)) {{
                            const ndvi = calcIndex(sample.B08, sample.B04);
                            if (!isNaN(ndvi)) {{
                                sumNDVI += ndvi;
                                count += 1;
                            }}
                        }}
                    }});
                    return count > 0 ? sumNDVI / count : null;
                }}

                const recentMeanNDVI = calculateMeanNDVI(recentIndices);
                const oldestMeanNDVI = calculateMeanNDVI(oldestIndices);

                const ndviDifference = (recentMeanNDVI !== null && oldestMeanNDVI !== null) 
                                        ? oldestMeanNDVI - recentMeanNDVI 
                                        : 0;

                if (ndviDifference >= NDVI_THRESHOLD) {{
                    return [1]; 
                }} else {{
                    return [0];
                }}
            }}
            """
        
        raise ValueError(f"Evalscript type '{script_type}' not supported.")