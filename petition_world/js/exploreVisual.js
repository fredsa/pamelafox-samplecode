var visualMarker;
jQuery(document).ready(function() {
        var map = "explore_map";
       if (location.pathname.toLowerCase().indexOf("vote") != -1){
          map = "vote_map";
       }
        var language = 'en_us';
        var maps = VOTEMAP.initialize(map, new GLatLng(55.6763, 12.5681), G_HYBRID_MAP, language);
        visualMarker = new MarkerManager(maps);
        //really really nasty hack 
        jQuery.getJSON("/info/continents", processContinents);
        VOTEMAP.startScan();
        });

function processContinents(json) {
          var info = json;
          var markers = [];
          for (continentCode in info.continents) {
            var continent = info.continents[continentCode];
            if (continent.count == 0) continue;
            var marker = new MarkerLight(new GLatLng(continent.center[0], continent.center[1]), createBigIcon(continent.count));
            marker.locationCode = continentCode;
            marker.title = continent.name
            markers.push(marker);
          }
          visualMarker.addMarkers(markers, 0, 3);
          visualMarker.show();
}

function createBigIcon(label) {
  var iconOptions = {};
  iconOptions.size = new GSize(64, 26);
  iconOptions.backgroundColor = "#ca6618";
  iconOptions.label = "" + label;
  return iconOptions;
}