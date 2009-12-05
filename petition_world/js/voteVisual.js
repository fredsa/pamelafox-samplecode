var nonce;
var geocodeInProgress;
var visitorId = null;
var visitorName = null;
var locationId = "global";
var maps;
var markerManager;
var loadedContinents;
var loadedCountries;

jQuery(document).ready(function() {
        var map = "explore_map";
       if (location.pathname.toLowerCase().indexOf("vote") != -1){
          map = "vote_map";
       }
       if (location.pathname.toLowerCase().indexOf("visual") != -1){
                map = "vote_map_wrapper";
        }
        var language = 'en_us';
        maps = VOTEMAP.initialize(map, new GLatLng(55.6763, 12.5681), G_HYBRID_MAP, language);
        voteMap = maps;
        markerManager = new MarkerManager(maps);
        //really really nasty hack 
        jQuery.getJSON("/info/continents", processContinents);
        VOTEMAP.startScan();
        jQuery(maps).bind("scanStopped", function(){
            markerManager = new MarkerManager(maps);
            GEvent.addListener(maps, "zoomend", handleZoomChange);
            GEvent.addListener(maps, "moveend", handleBoundsChange);
            });
        });
