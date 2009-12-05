jQuery(document).ready(function() {
        var map = "explore_map";
       if (location.pathname.toLowerCase().indexOf("vote") != -1){
          map = "vote_map"
       }
       
        var language = 'en_us';
        var votemap = VOTEMAP.initialize(map, new GLatLng(55.6763, 12.5681), G_HYBRID_MAP, language);
        VOTEMAP.startScan();
});
