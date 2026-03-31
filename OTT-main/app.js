require([
  "esri/layers/GraphicsLayer",
  "esri/widgets/Sketch/SketchViewModel",
  "utils/miscellaneous.js",
  "functions/CreateMap.js",
  "functions/DrawAoi.js",
  "functions/UploadAoi.js",
  "functions/MapDeforestation.js",
  "functions/TimeSeries.js",
  "functions/ChangeDetection.js",
  "functions/Downloadpolygon.js",
  "functions/DownloadBurnsZones.js"
], function (
  GraphicsLayer,
  SketchViewModel,
  miscellaneous,
  CreateMap,
  DrawAoi,
  UploadAoi,
  MapDeforestation,
  TimeSeries,
  ChageDetection,
  DownloadPolygon,
  DownloadBurnsZones
) {
  const [map, view] = CreateMap.createMap();
  let aoiGeometry;
  const graphicsLayer = new GraphicsLayer({ listMode: "hide" });
  map.add(graphicsLayer);

  const sketchViewModel = new SketchViewModel({
    view: view,
    layer: graphicsLayer,
    polygonSymbol: miscellaneous.graphicsSymbol,
  });
  // Add buttons to map view
  const drawAoiButton = document.getElementById("drawButton");
  const timeSeriesButton = document.getElementById("timeSeriesButton");
  const subsButton = document.getElementById("planetSubsButton");
  const uploadGeoJsonButton = document.getElementById("uploadGeoJsonButton");
  const mapDeforestationButton = document.getElementById("deforestationButton");
  const DownloadPolygonButton = document.getElementById("downloadpolButton");
  const mapBurnsButton = document.getElementById("downloadpolBurnsButton");
  
  view.ui.add(
    [
      drawAoiButton,
      uploadGeoJsonButton,
      timeSeriesButton,
      mapDeforestationButton,
      subsButton,
      DownloadPolygonButton,
      mapBurnsButton

    ],
    "top-right"
  );

  drawAoiButton.addEventListener("click", () => {
    DrawAoi.startDrawing(sketchViewModel, graphicsLayer, timeSeriesButton,mapDeforestationButton ,DownloadPolygonButton)
      .then((geometry) => {
        aoiGeometry = geometry;
        timeSeriesButton.disabled = false;
        mapDeforestationButton.disabled = false; 
        DownloadPolygonButton.disabled = false;
        mapBurnsButton.disabled = false;
      })
      .catch((error) => {
        console.error("Error drawing AOI:", error);
      });
  });

  uploadGeoJsonButton.addEventListener("click", () => {
    document.getElementById("browseGeoJson").click();
  });

  // Function to handle GeoJSON file upload and add to graphics layer
  document.getElementById("browseGeoJson").addEventListener("change", (event) =>
    UploadAoi.browseGeoJson(event, graphicsLayer, timeSeriesButton)
      .then((geometry) => {
        aoiGeometry = geometry;
        timeSeriesButton.disabled = false;
        DownloadPolygonButton.disabled = false;
        mapBurnsButton.disabled = false;
      })
      .catch((error) => {
        console.error("Error uploading AOI:", error);
      })
  );

  mapDeforestationButton.addEventListener("click", async () =>
    MapDeforestation.processImage(map, aoiGeometry)
  );

  timeSeriesButton.addEventListener("click", () =>
    TimeSeries.createTimeSeries(view, aoiGeometry)
  );

  subsButton.addEventListener("click", async () =>
    ChageDetection.getSubscriptionsData(map, view)
  );

  DownloadPolygonButton.addEventListener("click", async () =>{
    DownloadPolygon.DownloadPolygon(view, aoiGeometry)
  }
  );
  mapBurnsButton.addEventListener("click", async () =>{
    DownloadBurnsZones.processImage(view, aoiGeometry)
  }
  );



});
