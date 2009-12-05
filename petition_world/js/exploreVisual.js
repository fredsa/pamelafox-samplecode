jQuery(document).ready(function() {
        var language = 'en_us';
        var votemap = VOTEMAP.initialize("explore_map", new GLatLng(55.6763, 12.5681), G_HYBRID_MAP, language);
        VOTEMAP.startScan();
});
