
/*  Create and manage the map with "scan and pan" feature */
/*
    To initialize the map:
        VOTEMAP.initialize(
                            votemap_wrapper_id:string, 
                            centre_latlng:GLatLng, 
                            map_type:GMapType, 
                            language:string,
                            content_type:string ("Recent" or "Popular"),
                            is_cube_version:boolean
                            );

    To start the scan:
        VOTEMAP.startScan();

    To stop the scan:
        VOTEMAP.stopScan();

    To use VOTEMAP functionality with other maps or map features:
        Option 1 - VOTEMAP.initialize returns the GMap object that it creates which can be further manipulated.
        Option 2 - If a GMap object is passed to VOTEMAP.initialize in the votemap_wrapper_id parameter, VOTEMAP will use this map instead of creating its own (centre_latlng and map_type will be ignored). In this case the header displaying counts will not be created.
*/
    
var VOTEMAP = function() {
    // private constants
    var SCAN_ZOOM = 3;
    var SCAN_INTERVAL = 8000;   // 8 seconds
    var MAX_MARKERS = 50;
    var YT_VIDEO_PREFIX = "http://www.youtube.com/watch?v=";
    var YT_THUMBNAIL_PREFIX = "http://img.youtube.com/vi/";
    var YT_THUMBNAIL_SUFFIX = "/default.jpg";
    var VOTE = {
        "en_us" : "VOTE"
    }
    // private variables
    var map = null;
    var geocoder = null;
    var markers = [];
    var scanner = null;
    var scan_interrupt_listener = null;
    var content_lang = "en_us";
    var current_data = null;
    var current_display_index = 0;
    var current_geocode_index = 0;
    var waiting_on_geocode = false;
    var delay_start = false;
    var show_totals = true;
    var cube_version = false;
    var content_type = "Recent";
    var ryv_icon = new GIcon();
    ryv_icon.image = "images/pin_raiseyourvoice2.png";
    ryv_icon.iconSize = new GSize(24,28);
    ryv_icon.iconAnchor = new GPoint(12,14);
    ryv_icon.infoWindowAnchor = new GPoint(12,2);
    var IE6 = navigator.appName.indexOf('Microsoft') != -1 && parseFloat(navigator.appVersion) < 7;

    // private functions
    function setTotals(numPeople, numQuestions, numVotes) {
        if (!show_totals) return;
        var html = ["<span class='header_counts'>", numPeople, "</span>people have submitted<span class='header_counts'>", numQuestions, "</span>questions and cast<span class='header_counts'>", numVotes, "</span>votes"];    // this needs to be translated
        document.getElementById("counts_display").innerHTML = html.join(" ");
    }
    function getData() {
        // request new data
/*        var scrpt = document.createElement("script");
        scrpt.type = "text/javascript";
        scrpt.src = "js/json.js";
        document.getElementsByTagName("head")[0].appendChild(scrpt);*/
        try {
            var url = (content_type == "Recent" ? "data/top50.json" : "data/top50.json");
            GDownloadUrl(url, returnData);
        }
        catch (e) {
            returnData(null, -1);
        }
    }
    function returnData(data, rc) {
        //console.log("data returned rc=" + rc);
        if (rc == 200 || rc == 0) {           
            // success -- save new data
            current_data = eval('(' + data + ')');
            // display totals
            if (current_data.hasOwnProperty("totals"))
                setTotals(current_data.totals.people, current_data.totals.questions, current_data.totals.votes);
        }
        // if error, re-use old data if it exists
        else if (current_data == null) {
            alert ("Error getting data");
            return;
        }
        // try to geocode the first item
        current_geocode_index = 0;
        geocodeNext();
    }
    function geocodeNext() {
        // get the data for the question to be geocoded
        while(!current_data.questions[current_geocode_index].hasOwnProperty("loc")) {
            current_geocode_index++;
            if (current_geocode_index >= current_data.questions.length) {
                getData();
                return;
            }
        }
        var q_data = current_data.questions[current_geocode_index];
        geocoder.getLatLng(q_data.loc, function(point) {
            if (point) {
                // success -- save point in question data object
                q_data.latlng = point;
                if (waiting_on_geocode) {
                    current_display_index = current_geocode_index;
                    waiting_on_geocode = false;
                    displayQuestion();
                    // if this is the first data load, start up the scanner
                    if (delay_start) {
                        delay_start = false;
                        initScanner();
                    }
                }
            }
            else {
                //console.log ("Could not geocode " + q_data.loc);
                // failed -- try next
                current_geocode_index++;
                if (current_geocode_index >= current_data.questions.length) {
                    getData();
                }
                else geocodeNext();
            }
        });
    }
    function displayQuestion() {
        //console.log("display Question " + current_display_index);
        var q_data = current_data.questions[current_display_index];
        createMarker(q_data);
        // geocode next
        current_geocode_index++;
        if (current_geocode_index >= current_data.questions.length) {
            getData();
        }
        else geocodeNext();
    }
    function createMarker(q_data) {
            //console.log("create marker");
            // create a marker and save it
            var mkr = new GMarker(q_data.latlng, {icon:ryv_icon});
            map.addOverlay(mkr);
            var infowin_html = buildInfoWindow(q_data);
            var infowin_opt = {
                    noCloseOnClick: true
                };
            if (q_data.hasOwnProperty("youtube_id")) {
                infowin_opt.maxContent = '<div style="text-align:center;margin:8px 10px 0 0;"><object width="640" height="420"><param name="movie" value="http://www.youtube.com/v/' + q_data.youtube_id + '&hl=en_US&fs=1&"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/' + q_data.youtube_id + '&hl=en_US&fs=1&" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="640" height="420"></embed></object></div>';
                if (q_data.hasOwnProperty("title"))
                    infowin_opt.maxTitle = q_data.title;
            }
            GEvent.addListener(mkr, "click", function(e) {
                mkr.openInfoWindowHtml(infowin_html, infowin_opt);
            });
            markers.push(mkr);
            // hide the previous marker
            if (markers.length > 1) {
                markers[markers.length-2].hide();
            }
            // manage marker array
            if (markers.length > MAX_MARKERS) {
                // remove the first x markers until length = max
                var condemned = markers.splice(0, markers.length-MAX_MARKERS);
                for (var i=0; i<condemned.length; i++) {
                    map.removeOverlay(condemned[i]);
                }
            }
            // open the "pan and scan" window (can't trigger 'click' event because that would stop scanning)
            mkr.openInfoWindowHtml(infowin_html, infowin_opt);
    }
    function buildInfoWindow(q_data) {
        var DARK_BLUE_TOP = "#184ec3";
        var LIGHT_BLUE_TOP = "#5d92c0";
        var DARK_BLUE_BOT = "#154ecf";
        var LIGHT_BLUE_BOT = "#598fbe";
        var html = [];
        html.push('<div id="question_infowin"><table cellpadding=0 cellspacing=0><tr>');
        if (q_data.hasOwnProperty("youtube_id")) {
            html.push('<td width="130" align="center"><div id="infowin_thumb" style="background-image:url(http://img.youtube.com/vi/');
            html.push(q_data.youtube_id);
            html.push('/default.jpg);" onclick="VOTEMAP.showVideo();"></div><a href="#" class="smaller_text" onclick="VOTEMAP.showVideo();">');
            html.push((q_data.title && q_data.title != "" ? q_data.title : "Play Video"));
            html.push('</a></td>');
        }
        else html.push('<td></td>');
        html.push('<td><div id="infowin_question_text" style="');
        if (!IE6)
            html.push('max-');
        html.push('width:340px;">');
        if (q_data.hasOwnProperty("stmt"))
            html.push(q_data.stmt);
        html.push('</div><div id="infowin_submitter" class="smaller_text">');
        html.push(q_data.name);
        html.push('<br />');
        html.push(q_data.loc);
        html.push('</div></td></tr><tr><td colspan=2>');
        html.push('<a href="');
        html.push(q_data.vote_url);
        html.push('" target="_blank" id="vote_button" class="cop15_sprite"><div id="vote_button_text">');
        html.push(VOTE[content_lang]);
//        html.push('VOTE');  // this needs to be translated
        html.push('</div></a><div id="vote_graphs"><table><tr><td><div class="vote_bar" style="background-color:');
        html.push(q_data.votes.pos_pct >= q_data.votes.neg_pct ? DARK_BLUE_TOP : LIGHT_BLUE_TOP);
        html.push(';"><div class="vote_bar_background" style="width:');
        html.push(100 - q_data.votes.pos_pct);
        html.push('%;"></div></div><div class="vote_bar" style="background-color:');
        html.push(q_data.votes.pos_pct >= q_data.votes.neg_pct ? DARK_BLUE_BOT : LIGHT_BLUE_BOT);
        html.push(';"><div class="vote_bar_background" style="width:');
        html.push(100 - q_data.votes.pos_pct);
        html.push('%;"></div></div></td><td><a href="');
        html.push(q_data.vote_url);
        html.push('" id="thumb_up_image" class="cop15_sprite" target="_blank"></a></td></tr><tr><td><div class="vote_bar" style="background-color:');
        html.push(q_data.votes.neg_pct > q_data.votes.pos_pct ? DARK_BLUE_TOP : LIGHT_BLUE_TOP);
        html.push(';"><div class="vote_bar_background" style="width:');
        html.push(100 - q_data.votes.neg_pct);
        html.push('%;"></div></div><div class="vote_bar" style="background-color:');
        html.push(q_data.votes.neg_pct > q_data.votes.pos_pct ? DARK_BLUE_BOT : LIGHT_BLUE_BOT);
        html.push(';"><div class="vote_bar_background" style="width:');
        html.push(100 - q_data.votes.neg_pct);
        html.push('%;"></div></div></td><td><a href="');
        html.push(q_data.vote_url);
        html.push('" id="thumb_down_image" class="cop15_sprite" target="_blank"></a></td></tr></table></div>');
        html.push('</td></tr></table>');
        html.push('</div>');
        return html.join('');
    }
    function hideAllMarkers() {
        for (var i=0; i<markers.length; i++) {
            markers[i].hide();
        }
    }
    function showAllMarkers() {
        for (var i=0; i<markers.length; i++) {
            markers[i].show();
        }
    }
    function initScanner() {
        scanner = setInterval(VOTEMAP.scanNext, SCAN_INTERVAL);
        // create listener to stop pan'n'scan when user interacts with map
        if (scan_interrupt_listener == null)
            scan_interrupt_listener = GEvent.addListener(map, "click", function(ov, ll, ov_ll) {
                VOTEMAP.stopScan();
            });
    }
    return {
        initialize: function(mapElem, initCentre, initType, language, mapContentType, cube) {
            // is this for the cube?
            if (cube) cube_version = cube;  // default is false

            // if the mapElem param is a string then create the map
            if (typeof mapElem == "string") {
                if (!mapElem || !initCentre || !initType) {
                    alert("Required map parameters not passed to VOTEMAP.initialize, cannot create map!");
                    return;
                }
                // create the header and map elements
                var wrapper = document.getElementById(mapElem);
                // note that for some reason have to set width and height of map here instead of css
                var display_html = '<div id="vote_map_header"><table width="100%"><tr><td align="left"><div id="counts_display"></div></td>';
                if (!cube_version)  // don't want the link for the cube
                    display_html += '<td align="right"><a href="#" onclick="VOTEMAP.swapType();return false;">Show Most <span id="content_type">Popular</span> Questions</a></td>';
                display_html += '</tr></table></div><div id="vote_map_canvas" style="width:100%; height:95%;"></div>';
                wrapper.innerHTML = display_html;

                // create the map
                if (!GBrowserIsCompatible()) return;
                map = new GMap2(document.getElementById("vote_map_canvas"));
                map.setCenter(initCentre, SCAN_ZOOM, initType);
                // don't need controls for the cube
                if (!cube_version) 
                    map.setUIToDefault();
            }
            else {  // a map was passed in
                // make sure it's a good map
                if (!mapElem.addControl) {
                    alert("Error! Map element is not valid");
                    return;
                }
                map = mapElem;
                show_totals = false;
            }
            // don't need controls for the cube
            if (!cube_version) {
                // add the scan'n'pan control
                map.addControl(new ScanNPanControl());

                // stop the scanning when zoom is changed
                GEvent.addListener(map, "zoomend", function(oz, nz) {   // funny--looks like Australia and New Zealand but is actually short for old-zoom and new-zoom 
                    if (scanner)
                        VOTEMAP.stopScan();
                });
            }
            geocoder = new GClientGeocoder();

            if (mapContentType)
                content_type = mapContentType;
            if (language)
                content_lang = language;

            // request data, returned data will start scan
            getData();
        },
        scanNext: function() {
            // check if the current question is geocoded already
            if (!current_data || !current_data.questions[current_geocode_index].hasOwnProperty("latlng")) {
                // if not, set flag to have it display as soon as geocode comes in
                //console.log("waiting on geocode");
                waiting_on_geocode = true;
            }
            else {
                // display most recently geocoded question
                current_display_index = current_geocode_index;
                displayQuestion();
            }
        },
        stopScan: function() {
            if (scanner != null) {
                clearInterval(scanner);
                scanner = null;
            }
            // remove listener when not needed
            if (scan_interrupt_listener != null) {
                GEvent.removeListener(scan_interrupt_listener);
                scan_interrupt_listener = null;
            }
            showAllMarkers();
            // update pause/play buttons
            if (!cube_version) {
                document.getElementById("startScan").className = "cop15_sprite";
                document.getElementById("stopScan").className += " selected";
            }
        },
        startScan: function() {
            hideAllMarkers();
            // reset zoom to scan level
            if (map.getZoom() != SCAN_ZOOM) map.setZoom(SCAN_ZOOM);
            if (scanner == null) {
                // if we have no data, delay the startup until we get some, otherwise the first is sometimes too slow
                if (!current_data) delay_start = true;
                else initScanner();
                // start with a new one right away
                VOTEMAP.scanNext();
            }
            // update pause/play buttons
            if (!cube_version) {
                document.getElementById("startScan").className += " selected";
                document.getElementById("stopScan").className = "cop15_sprite";
            }
        },
        swapType: function() {
            //console.log("swap type");
            var old_type = content_type;
            if (content_type == "Recent")
                content_type = "Popular";
            else content_type == "Recent";

            VOTEMAP.stopScan();
            map.clearOverlays();
            current_data = null;
            getData();
            if (!cube_version && show_totals) 
                document.getElementById("content_type").innerHTML = old_type;
            VOTEMAP.startScan();
        },
        showVideo: function() {
            var iwin = map.getInfoWindow();
            iwin.maximize();
        }
    }
}();

    
