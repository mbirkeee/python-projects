from password import GOOGLE_MAPS_KEY_OLD as GOOGLE_MAPS_KEY

TOP = """
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>%s</title>
    <style>
      /* Always set the map height explicitly to define the size of the div
       * element that contains the map. */
      #map {
        height: 100%%;
      }
      /* Optional: Makes the sample page fill the window. */
      html, body {
        height: 100%%;
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

    /*
      google.maps.event.addListener(map, 'mousemove', function (event) {
              displayCoordinates(event.latLng);
          });
    */
      google.maps.event.addListener(map, 'click', function (event) {
              displayCoordinates(event.latLng);
          });

      function displayCoordinates(pnt) {
          var lat = pnt.lat();
          lat = lat.toFixed(6);
          var lng = pnt.lng();
          lng = lng.toFixed(6);
          console.log("{ KEY.LAT : " + lat + ", KEY.LNG : " + lng + " },");
      }
"""

CIRCLE = """
for (var point in circle) {
  var circ = new google.maps.Circle({
    strokeColor: '%s',
    strokeOpacity: %f,
    strokeWeight: %d,
    fillColor: '%s',
    fillOpacity: %f,
    map: map,
    center: circle[point].center,
    radius: %d,
  });
  circ.setMap(map);

   /*
  google.maps.event.addListener(circ, 'mousemove', function (event) {
    displayCoordinates(event.latLng);
  });
  */
  google.maps.event.addListener(circ, 'click', function (event) {
    displayCoordinates(event.latLng);
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

/*
google.maps.event.addListener(mark, 'mousemove', function (event) {
    displayCoordinates(event.latLng);
});
*/

google.maps.event.addListener(mark, 'click', function (event) {
    displayCoordinates(event.latLng);
  });
"""

POLYGON = """
var my_polygon = new google.maps.Polygon({
  paths: polypoints,
  strokeColor: '%s',
  strokeOpacity: %f,
  strokeWeight: %d,
  fillColor: '%s',
  fillOpacity: %f
});
my_polygon.setMap(map);
"""

POLYGON_LATLON = """
var my_polygon = new google.maps.Polygon({
  paths: polypoints,
  strokeColor: '%s',
  strokeOpacity: %f,
  strokeWeight: %d,
  fillColor: '%s',
  fillOpacity: %f
});
my_polygon.setMap(map);

google.maps.event.addListener(my_polygon, 'mousemove', function (event) {
    displayCoordinates(event.latLng);
});
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


# ROUTE_TOP = """
# <!DOCTYPE html>
# <html>
#   <head>
#     <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
#     <meta charset="utf-8">
#     <title>Trip Map</title>
#     <style>
#       /* Always set the map height explicitly to define the size of the div
#        * element that contains the map. */
#       #map {
#         height: 100%;
#       }
#       /* Optional: Makes the sample page fill the window. */
#       html, body {
#         height: 100%;
#         margin: 0;
#         padding: 0;
#       }
#     </style>
#   </head>
#   <body>
#     <div id="map"></div>
#     <script>
#
#       function initMap() {
#         var map = new google.maps.Map(document.getElementById('map'), {
#           zoom: 13,
#           center: {lat: 52.10, lng: -106.65},
#           mapTypeId: 'terrain'
#         });
#
#         var flightPlanCoordinates = [
# """

# ROUTE_MIDDLE = """
#         ];
#         var flightPath = new google.maps.Polyline({
#           path: flightPlanCoordinates,
#           geodesic: true,
#           strokeColor: '#0000FF',
#           strokeOpacity: 1.0,
#           strokeWeight: 2
#         });
#
#         flightPath.setMap(map);
#         var trip = {
# """

POLYLINE = """
var flightPath = new google.maps.Polyline({
  path: polyline,
  geodesic: true,
  strokeColor: '%s',
  strokeOpacity: %f,
  strokeWeight: %d
});
flightPath.setMap(map);
"""

# ROUTE_BOTTOM = """
#         };
#
#         for (var point in trip) {
#           var circle = new google.maps.Circle({
#             strokeColor: trip[point].color,
#             strokeOpacity: 1,
#             strokeWeight: 2,
#             fillColor: trip[point].color,
#             fillOpacity: 1,
#             map: map,
#             center: trip[point].center,
#             radius: 30
#           });
#         }
#       }
#     </script>
#     <script async defer
#       src="https://maps.googleapis.com/maps/api/js?key=%s&callback=initMap">
#     </script>
#   </body>
# </html>
# """ % GOOGLE_MAPS_KEY
