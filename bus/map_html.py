from password import GOOGLE_MAPS_KEY_OLD as GOOGLE_MAPS_KEY

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
          zoom: 13,
          center: {lat: 52.125, lng: -106.65},
          mapTypeId: 'terrain'
        });
"""

CIRCLE_RED_20 = """
for (var point in circle) {
  var circ = new google.maps.Circle({
    strokeColor: '#FF0000',
    strokeOpacity: 0.25,
    strokeWeight: 1,
    fillColor: '#FF0000',
    fillOpacity: 0.25,
    map: map,
    center: circle[point].center,
    radius: 20,
  });
}
"""

MARKER = """
for (var point in marker) {
  var mark = new google.maps.Marker({
    position: marker[point].center,
    map: map,
    title: marker[point].title,
    label: marker[point].label,
  });
}
"""

# MARKER1 = """
# for (var point in marker) {
#   var marker = new google.maps.Marker({
#     position: new google.maps.LatLng(marker[point].center),
#     map: map,
#     title: marker[point].title,
#     label: marker[point].label,
#   });
# }
# """


CIRCLE_RED_50 = """
for (var point in circle) {
  var circ = new google.maps.Circle({
    strokeColor: '#FF0000',
    strokeOpacity: 0.25,
    strokeWeight: 1,
    fillColor: '#FF0000',
    fillOpacity: 0.25,
    map: map,
    center: circle[point].center,
    radius: 50
  });
}
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
    src="https://maps.googleapis.com/maps/api/js?key=%s&libraries=visualization&callback=initMap">
    </script>
  </body>
</html>
""" % GOOGLE_MAPS_KEY


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
          strokeColor: '#0000FF',
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
            strokeColor: trip[point].color,
            strokeOpacity: 1,
            strokeWeight: 2,
            fillColor: trip[point].color,
            fillOpacity: 1,
            map: map,
            center: trip[point].center,
            radius: 30
          });
        }
      }
    </script>
    <script async defer
      src="https://maps.googleapis.com/maps/api/js?key=%s&callback=initMap">
    </script>
  </body>
</html>
""" % GOOGLE_MAPS_KEY
