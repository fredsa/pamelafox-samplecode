<html>
<head><title>My Map -> Encoded Polys -> Static Maps</title>
<link rel="stylesheet" type="text/css" href="http://code.google.com/css/dev_docs.css"> 
</head>
<body>
<h2>My Maps -> Static Map Converter</h2>

<p>To use this, pass the ID of the My Map via the "&id=" parameter.
It will turn the markers, paths, and polygons into a static map, using the 
<a href="http://code.google.com/apis/maps/documentation/staticmaps/">Static Maps API v2</a>.
Keep in mind that many browsers have a max URL length for images, so you don't
want to render too many paths on a static map image.
</p>
<p>You can try these IDs:</p>
<ul>
<li>Sydney blackout: 109250181535574469723.0004665074a7b33dd9869</li>
<li>Test Map: 109250181535574469723.00047209aa022982954a2</li>
</ul>

<hr>

<?php

include("PolylineEncoder.php");

if(isset($_GET["id"])) {
  $mapId = $_GET["id"];
} else {
  $mapId = "109250181535574469723.0004665074a7b33dd9869";
}

$mapUrl = "http://maps.google.com/maps/ms?ie=UTF8&hl=en&msa=0&output=kml&msid=" . $mapId;

echo "<p>Parsing: <a href=\"" . $mapUrl . "\">" . $mapUrl . "</a></p>";

$xml = simplexml_load_file($mapUrl) or die("url not loading");

$staticMapUrl = "http://maps.google.com/maps/api/staticmap?size=400x400";

echo "<ul>";
foreach($xml->Document->Placemark as $placemark) {
  $points = array();
  $name = $placemark->name;
  echo "<li>" . $name . " : <ul>";
  if ($placemark->Polygon) {
    $coords = $placemark->Polygon->outerBoundaryIs->LinearRing->coordinates;
    $parsedCoords = parseCoords($coords);
    $staticMapUrl .= "&path=fillcolor:0x0000FF33|enc:" . $parsedCoords[0];
  } else if ($placemark->LineString) {
    $coords = $placemark->LineString->coordinates;
    $parsedCoords = parseCoords($coords);
    $staticMapUrl .= "&path=enc:" . $parsedCoords[0];
  } else if ($placemark->Point) {
    $coords = $placemark->Point->coordinates;
    $parsedCoords = parseCoords($coords);
    $staticMapUrl .= "&markers=" . $parsedCoords[1][0][0] . "," . $parsedCoords[1][0][1];
  }
  echo "</ul></li>";
}
echo "</ul>";

$staticMapUrl .= "&sensor=false&key=ABQIAAAA-O3c-Om9OcvXMOJXreXHAxTPZYElJSBeBUeMSX5xXgq6lLjHthQK56gfyM5NBqKVAIOX7Pg8-ceW5A";
echo "<p><img src=\"" . $staticMapUrl . "\"></p>";

function parseCoords($coords) {
  $points = array();
  $polylineEncoder = new PolylineEncoder();
  $coordsArray = preg_split("/[\s]+/", $coords);
  $numPoints = 0;
  echo "<li>Points: ";
  for ($i = 0; $i < count($coordsArray); $i++) {
    $latlngArray = split(",", $coordsArray[$i]);
    if (count($latlngArray) == 3) {
      $points[$numPoints] = array();
      $lat = floatval($latlngArray[1]);
      $lng = floatval($latlngArray[0]);
      $points[$numPoints][0] = $lat;
      $points[$numPoints][1] = $lng;
      echo $lat . ", " . $lng . " ";
      $numPoints++;
    }
  }
  $polyline = $polylineEncoder->dpEncode($points);
  echo "<li>Encoded string: " .  $polyline[0] . "</li>";
  $results = array($polyline[0], $points);
  return $results;
}

?>
