TOP = """
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>Bus Maps</title>
    <style>
      /* Always set the map height explicitly to define the size of the div
       * element that contains the map. */
      #map {
        height: 100%;
      }
      /* Optional: Makes the sample page fill the window. */
      html, body {
        height: 100%;
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <div id="map"></div>
    <script>

      function initMap() {
        var map = new google.maps.Map(document.getElementById('map'), {
          zoom: 12,
          center: {lat: 52.2, lng: -106.65},
          mapTypeId: 'terrain'
        });
"""


CIRCLE1 = """
for (var point in circle1) {
  var circle = new google.maps.Circle({
    strokeColor: '#FF0000',
    strokeOpacity: 0.25,
    strokeWeight: 1,
    fillColor: '#FF0000',
    fillOpacity: 0.25,
    map: map,
    center: circle1[point].center,
    radius: 100
  });
}
"""

CIRCLE2 = """
for (var point in circle2) {
  var circle = new google.maps.Circle({
    strokeColor: '#0000FF',
    strokeOpacity: 0.25,
    strokeWeight: 1,
    fillColor: '#0000FF',
    fillOpacity: 0.25,
    map: map,
    center: circle2[point].center,
    radius: 2
  });
}
"""

BOTTOM = """
      }
    </script>
    <script async defer
    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBlabwKhgVWHc5Yfr3bUYGSUDJyYTKX5QY&callback=initMap">
    </script>
  </body>
</html>

"""




ROUTE_TOP = """
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>Trip Map</title>
    <style>
      /* Always set the map height explicitly to define the size of the div
       * element that contains the map. */
      #map {
        height: 100%;
      }
      /* Optional: Makes the sample page fill the window. */
      html, body {
        height: 100%;
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <div id="map"></div>
    <script>

      function initMap() {
        var map = new google.maps.Map(document.getElementById('map'), {
          zoom: 13,
          center: {lat: 52.10, lng: -106.65},
          mapTypeId: 'terrain'
        });

        var flightPlanCoordinates = [
"""

ROUTE_MIDDLE = """
        ];
        var flightPath = new google.maps.Polyline({
          path: flightPlanCoordinates,
          geodesic: true,
          strokeColor: '#FF0000',
          strokeOpacity: 1.0,
          strokeWeight: 2
        });

        flightPath.setMap(map);
        var trip = {
"""


ROUTE_BOTTOM = """
        };


        for (var point in trip) {
          var circle = new google.maps.Circle({
            strokeColor: '#0000FF',
            strokeOpacity: 0.25,
            strokeWeight: 2,
            fillColor: '#0000FF',
            fillOpacity: 0.25,
            map: map,
            center: trip[point].center,
            radius: 30
          });
        }
      }
    </script>
    <script async defer
    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBlabwKhgVWHc5Yfr3bUYGSUDJyYTKX5QY&callback=initMap">
    </script>
  </body>
</html>

"""