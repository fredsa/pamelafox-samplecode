//need a better way to handle these
google.load('friendconnect', '0.8');
google.load("search", "1.0");



var VoteController = function() {
    var voteControl;
    var map = null;
     return {
         setMap: function(globalMap)
         {
             map = globalMap;
         },
         
        showVote: function() 
        {
                     voteControl = new earthHourVoteControl();
                     map.addControl(voteControl);  
                     jQuery(map).trigger("voteControlAdded");
        },
        closeVote: function()
        {
            map.removeControl(voteControl);
        }
     };
}();



var MapManager = function(param) {
    var params = param;
    var map;
    var toggler = 0;
    var markerManager;
    var processHandlers;
    var pageTypes = {};
    var language = "en_us";
    var voteControl;
    var util = new Util();
    var orgs = null;
    var nonce;
    var voteControlButton;


    this.showVoteControl = function()
    {
         map.removeControl(voteControlButton);
         VoteController.showVote();
    };
    var editParamsFromQuery = function()
    {
        params.voteControl = getQueryValue(params.voteControl,util.getParameterByName('voteControl'));
        params.includeVoteMarkers = getQueryValue(params.includeVoteMarkers,util.getParameterByName('includeVoteMarkers'));
        params.includeSearch = getQueryValue(params.includeSearch,util.getParameterByName('includeSearch'));
        params.voteControl = getQueryValue(params.voteControl,util.getParameterByName('voteControl'));
        params.startScan = getQueryValue(params.startScan,util.getParameterByName('startScan'));
        params.visual = getQueryValue(params.visual,util.getParameterByName('visual'));
        params.showTotals =getQueryValue(params.visual,util.getParameterByName('showTotals'));
    };
    var getQueryValue = function(param,value)
    {
        if(value == '')
            return param;
        else if(value.toUpperCase() == 'TRUE' )
            return true;
        
        return false;
    };
    
    var animateTotals = function() {
        if (toggler == 0) {
            jQuery('#votes_span').toggle();
            //toggle off
            jQuery('#countries_span').toggle();
            //toggle on
            toggler = 1;
        }
        else if (toggler == 1) {
            jQuery('#countries_span').toggle();
            //toggle off
            jQuery('#orgs_span').toggle();
            // toggle on
            toggler = 2;
        }
        else if (toggler == 2) {
            jQuery('#orgs_span').toggle();
            //toggle off
            jQuery('#votes_span').toggle();
            //toggle on
            toggler = 0;
        }
    };

    var setUpMarkerManager = function()
    {
        markerManager = new MarkerManager(map);
        return markerManager;
    };

    var setUpMap = function()
    {
        
        if (params.visual)
        {
     
            if (params.useMapObject)
            {
                map = new GMap2(jQuery(params.map)[0]);
                map.setCenter(new GLatLng(0, 10), 1, G_HYBRID_MAP);
                map.setUIToDefault();
                map = VOTEMAP.initialize(map, new GLatLng(55.6763, 12.5681), G_HYBRID_MAP, language, 'Recent',false);
            }
            else
            {
                map = VOTEMAP.initialize(params.map, new GLatLng(55.6763, 12.5681), G_HYBRID_MAP, language,'Recent',false);
            }
            if (params.startScan)
            {
                VOTEMAP.startScan();
            }
        }
        else
        {
            if (typeof params.map == "string") {
                map = new GMap2(jQuery(params.map)[0]);
                map.setCenter(new GLatLng(0, 10), 1, G_PHYSICAL_MAP);
                map.setUIToDefault();
            }
            else if (params.map)
            {
                map = params.map;
            }
            else
            {
                alert('Please specify a valid map');
            }
        }
         jQuery(map).bind("voteControlAdded", function()
            {
                setUpVotePage();
            });
        VoteController.setMap(map);
        if(params.voteControl)
        {
         voteControlButton = new earthHourVote();
         map.addControl(voteControlButton);
        
        }
        return map;
    };
    

    
    this.closeVoteControl = function()
    {
         VoteController.closeVote();
         //the VoteController class should really be handling this stuff
         map.addControl(voteControlButton);
    };

    var setUpExplorePage = function()
    {

        var visitorId = null;
        var visitorName = null;

        google.friendconnect.container.setParentUrl('/gfc/');
        if(typeof(params.includeVoteMarkers) == 'undefined') {
            params.includeVoteMarkers = true;
        }
        if(params.includeVoteMarkers)
        {
            GEvent.addListener(map, "zoomend", processHandlers.handleZoomChange);
            GEvent.addListener(map, "moveend", processHandlers.handleBoundsChange);
            processHandlers.handleZoomChange();
            processHandlers.handleBoundsChange();
        }
        //TODO: add a param to turn this on and off
        GEvent.addListener(map, "infowindowopen",
        function() {
            var iw = map.getInfoWindow();
            window.setTimeout(function() {
                iw.maximize();
            },
            5);

            GEvent.addListener(iw, "maximizeend",
            function() {
                var skin = {};
                skin['BORDER_COLOR'] = '#cccccc';
                skin['ENDCAP_BG_COLOR'] = util.getSiteBG(params.skin);
                skin['ENDCAP_TEXT_COLOR'] = '#333333';
                skin['ENDCAP_LINK_COLOR'] = '#0000cc';
                skin['ALTERNATE_BG_COLOR'] = '#ffffff';
                skin['CONTENT_BG_COLOR'] = '#ffffff';
                skin['CONTENT_LINK_COLOR'] = '#0000cc';
                skin['CONTENT_TEXT_COLOR'] = '#333333';
                skin['CONTENT_SECONDARY_LINK_COLOR'] = '#7777cc';
                skin['CONTENT_SECONDARY_TEXT_COLOR'] = '#666666';
                skin['CONTENT_HEADLINE_COLOR'] = '#333333';
                skin['DEFAULT_COMMENT_TEXT'] = '- add your comment here -';
                skin['HEADER_TEXT'] = 'Show your support of the vote in ' + currentMarker.title;
                skin['POSTS_PER_PAGE'] = '4';
                skin['HEIGHT'] = '330';
                google.friendconnect.container.renderWallGadget({
                    id: 'div-864264044956702366',
                    site: site_id,
                    'view-params': {
                        "disableMinMax": "true",
                        "scope": "ID",
                        "features": "video,comment",
                        "allowAnonymousPost": "true",
                        "docId": SHA1Digest(currentMarker.markerType + currentMarker.locationCode + currentMarker.title),
                        "startMaximized": "true",
                        "useFixedHeight": "true"
                    }
                },
                skin);
            });
        });

        google.friendconnect.container.initOpenSocialApi({
            site: site_id,
            onload: function(securityToken) {
                var req = opensocial.newDataRequest();
                req.add(req.newFetchPersonRequest('VIEWER'), 'viewer');
                req.send(function(response) {
                    var data = response.get('viewer').getData();
                    if (data) {
                        visitorId = data.getId();
                        visitorName = data.getDisplayName();
                        var nameField = jQuery('#person_name');
                        if (nameField.val() == null || nameField.val().replace(/^\s+|\s+$/g, '') == '') {
                            nameField.val(visitorName);
                        }
                        var gfcIdField = jQuery('#person_gfc_id');
                        gfcIdField.val(visitorId);
                    } else {
                        // Not logged in
                        visitorId = null;
                        visitorName = null;
                    }
                });
            }
        });


    };

    var loadNonce = function() {
      if (!nonce) {
        jQuery.getJSON('/nonce', function (data) {
          nonce = data['nonce'];
          if (nonce) {
            jQuery('#nonce').val(SHA1Digest(nonce));
          } else {
            alert("Missing nonce, cannot submit form successfully.");
          }
        })
      }
    }

    var setUpVotePage = function()
    {
        loadNonce();
        jQuery('.org').hide();
        jQuery("#form_toggle").change(processHandlers.toggleForm);
        jQuery('#sign').validate({
            //overwrite to change the way errors are reported
            //the extra space was kinda hard to fit in the new forms 
          showErrors: function(errorMap, errorList) {
                  if (errorList.length > 0) {
                      $(errorList).each(function() {
                          $("[for='" +this.element.name + "']").addClass(" Error");
                      });
                  } else {
                      $(this.lastElement).each(function() {
                          $("[for='" + this.id + "']").removeClass("Error");
                      });
                  }           
        }});
        jQuery('#country').change(processHandlers.performFormsGeoCode);
        jQuery('#state').change(processHandlers.performFormsGeoCode);
        jQuery('#city').change(processHandlers.performFormsGeoCode);
        jQuery('#postcode').change(processHandlers.performFormsGeoCode);
        jQuery('#streetinfo').change(processHandlers.performFormsGeoCode);
        jQuery('#city').keypress(processHandlers.performFormsGeoCode);
        jQuery('#postcode').keypress(processHandlers.performFormsGeoCode);
        processHandlers.populateCountries();
    };

    this.moveMap = function(zoom)
    {
        if (!zoom)
        {
            zoom = 1;
        }
        var point = new GLatLng(latlng.split(',')[0], latlng.split(',')[1]);
        map.setCenter(point, zoom);
    };


    var showTotals = function()
    {
        if (params.showTotals)
        {
            window.setInterval(animateTotals, 4000);
            jQuery.getJSON("/info/totals", processHandlers.processTotals);
        }
    };

    var addMarkers = function()
    {


        };

    var setPageDict = function()
    {
        pageTypes.vote = setUpVotePage;
        pageTypes.explore = setUpExplorePage;
        return pageTypes;
    };

    
    var setUpSearch = function()
    {
        if (params.includeSearch)
        {
            jQuery.getJSON("/info/orgName",
            function(data, text)
            {
                processHandlers.addOrgs(data);
            });
            jQuery("#searchButton").click(processHandlers.searchnNearOrgs);

            jQuery('#searchInput').click(function()
            {
                if (jQuery('#searchInput').val() == 'search the map')
                jQuery('#searchInput').val('')
            });

            jQuery('#searchInput').keydown(function()
            {
                if ($("#searchButton").val() == "Cancel")
                {
                    $("#searchButton").val("Search");
                }
            });
        }
        else
        {
            $("#MapTop").hide();
            $(params.map).height($("#show_your_vote").height());
            map.checkResize();
        }
    };

    var init = function()
    {
        editParamsFromQuery();
        setPageDict();
        processHandlers = new Processors(setUpMap(), setUpMarkerManager(),params.RYV);
        showTotals();
        setUpSearch();
        pageTypes[params.page]();
        if(params.hasForm)
        {
            pageTypes['vote']();
        }
        addMarkers();
    }();
};

var Processors = function(map, markers,skin)
 {
    var markerManager = markers;
    
    var markerCreator = new MarkerCreator(map,skin);
    var map = map;
    var loadedCountries = false;
    var loadedContinents = false;
    var orgs;
    var geocodeInProgress;

    this.addOrgs = function(searchOrgs)
    {
        orgs = searchOrgs;
    };

    this.processTotals = function(json) {
        jQuery("#votes").html(json.total.totalVotes);
        jQuery("#countries").html(json.total.totalCountries);
        jQuery("#orgs").html(json.total.totalOrgs);
    };

    var processContinents = function(json) {
        var info = json;
        var markers = [];
        for (continentCode in info.continents) {
            var continent = info.continents[continentCode];
            if (continent.count == 0) continue;
            var marker = markerCreator.createMarker("continent", continentCode, new GLatLng(continent.center[0], continent.center[1]), markerCreator.createBigIcon(continent.count), continent.name, 3);
            markers.push(marker);
        }
        markerManager.addMarkers(markers, 0, 3);
        markerManager.refresh();
    };

    var processCountries = function(json) {
        var info = json;
        var markers = [];
        for (countryCode in info.countries) {
            var country = info.countries[countryCode];
            var marker = markerCreator.createMarker("country", countryCode, new GLatLng(country.center[0], country.center[1]), markerCreator.createBigIcon(country.count), country.name, 6);
            markers.push(marker);
        }
        markerManager.addMarkers(markers, 3, 7);
        markerManager.refresh();
    };

    var processStates = function(json) {
        var info = json;
        var markers = [];
        for (stateCode in info.states) {
            var state = info.states[stateCode];
            var marker = markerCreator.createMarker("state", stateCode, new GLatLng(state.center[0], state.center[1]), markerCreator.createMediumIcon(state.count), state.name, 6);
            markers.push(marker);
        }
        markerManager.addMarkers(markers, 4, 7);
        markerManager.refresh();
    };

    this.performFormsGeoCode =function() {
      var country = jQuery('#country option:selected').text();
      if (country != null && country.replace(/^\s+|\s+$/g, '') != '') {
        // They've set their country, we can geocode something.
        // TODO: Do fewer geocodes.
        setTimeout(function () {
          var streetinfo = jQuery('#streetinfo').val();
          var state = jQuery('#state').val();
          var city = jQuery('#city').val();
          var postcode = jQuery('#postcode').val();
          var geocoder = new GClientGeocoder();
          var locationString;
          locationString = streetinfo + ", " + city + ", " + state + " " + postcode + ", " + country;
          if (!geocodeInProgress || locationString != geocodeInProgress) {
            geocoder.getLatLng(locationString, latLngHandler);
            geocodeInProgress = locationString;
          }
        }, 100);
      }
    };
    
    this.populateCountries = function() {
      jQuery('.state').hide();
      var countrySelect = jQuery('#country');
      countrySelect.change(this.populateStates);
      for (var countryCode in countriesInfo) {
        var countryOption = jQuery(document.createElement('option'));
        countryOption.val(countryCode);
        countryOption.text(countriesInfo[countryCode].name);
        countrySelect.append(countryOption);
      }
    };

    this.populateStates = function() {
      var countryCode = jQuery('#country').val();
      if (countriesInfo[countryCode].hasStates) {
        jQuery('.state').show();
        var states = countriesInfo[countryCode].states;
        jQuery('#state').rules('add', {required: true});
        jQuery('#state').html('');
        for (var i = 0; i < states.length; i++) {
          var stateOption = jQuery(document.createElement('option'));
          stateOption.val(states[i]);
          stateOption.text(states[i]);
          jQuery('#state').append(stateOption);
        }
      } else {
        jQuery('.state').hide();
        jQuery('#state').rules('remove');
      }

      var postcodeInput = jQuery('#postcode');
      if (countriesInfo[countryCode].hasPostcodes) {
        jQuery('.postcode').show();
        jQuery('#postcode').rules('add', {required: true});
      } else {
        jQuery('.postcode').hide();
        jQuery('#postcode').rules('remove');
      }
    }
    
    
    this.toggleForm = function() {
      formValue =  $("#form_toggle").val();
      if (formValue == 'org') {
        jQuery('#email').rules('add', {required: true});
        jQuery('#streetinfo').rules('add', {required: true});
        jQuery('#org_name').rules('add', {required: true});
        jQuery('.person').hide();
        jQuery('.org').show();
      } else {
        jQuery('.org').hide();
        jQuery('#email').rules('remove');
        jQuery('#streetinfo').rules('remove');
        jQuery('#org_name').rules('remove');
        jQuery('.person').show();
      }
    };
    
    var processPostcodes = function(json) {

        var info = json;
        var markers = [];
        for (postcodeCode in info.postcodes) {
            var postcode = info.postcodes[postcodeCode];
            var marker = markerCreator.createMarker("postcode", postcodeCode, new GLatLng(postcode.center[0], postcode.center[1]), markerCreator.createSmallIcon(postcode.count), postcodeCode, 14);
            markers.push(marker);
        }

        markerManager.addMarkers(markers, 8);
        markerManager.refresh();
    };

    this.latLngHandler = function(point) {
      if (!point) {
        //geoError();
      } else {
        map.clearOverlays();
        map.setCenter(point, 11);
        var marker = new GMarker(point);
        voteMap.addOverlay(marker);
        jQuery('#lat').val(point.lat());
        jQuery('#lng').val(point.lng());
        jQuery('#submit').removeAttr('disabled');
      }
    };
    
    var processOrgs = function(json) {
        var orgs = json.orgs;
        var markers = [];

        /*
      for (var i = 0; i < orgs.length; i++) {
          var marker = createSmallOrgMarker(orgs[i]);
          markers.push(marker);
        }
        markerManager.addMarkers(markers, 5, 8); // 0 is the coarsest setting, full world view
      */
        markers = [];
        for (var i = 0; i < orgs.length; i++) {
            if (orgs[i].icon.length > 20) {
                var marker = markerCreator.createMedOrgMarker(orgs[i]);
                markers.push(marker);
            }
        }
        markerManager.addMarkers(markers, 10, 13);
        // 0 is the coarsest setting, full world view
        markers = [];
        for (var i = 0; i < orgs.length; i++) {
            if (orgs[i].icon.length > 20) {
                var marker = markerCreator.createOrgMarker(orgs[i]);
                markers.push(marker);
            }
        }
        markerManager.addMarkers(markers, 14);
        // 0 is the coarsest setting, full world view
        markerManager.refresh();
    };


    this.searchnNearOrgs = function(name) {
        var orgName = jQuery("#searchInput").val();
            if (jQuery.inArray(orgName.toUpperCase(), orgs) > -1)
            {
                ;
                var bounds = exploreMap.getBounds();
                /*
           this is not longer needed, but may be useful code if the search does not function as desired
           So going to leave it in, for at least one check in
          var countryCodes = [];
          for (countryCode in countriesInfo) {
            var countryInfo = countriesInfo[countryCode];
            var countryBounds = new GLatLngBounds(new GLatLng(countryInfo.bounds.southWest[0], countryInfo.bounds.southWest[1]), new GLatLng(countryInfo.bounds.northEast[0], countryInfo.bounds.northEast[1]));
            if (bounds.intersects(countryBounds)) {
               countryCodes.push(countryCode);
            }
          }
          */
                var arguments = {}
                //name to search for
                arguments.name = orgName;
                //current view, get center use haversine to poll based on radius rather than bounds
                //arguments.bounds =  exploreMap.getBounds();
                //country codes we are looking at
                //more app enginy way to do this? rpc? or encode a json string and use djangos simplejson lib
                //arguments.countryCode = countryCodes.join('|');
                jQuery.getJSON('/info/search', arguments,
                function(data, status)
                {
                    $("#searchButton").val("Cancel");
                    var bounds = new google.maps.LatLngBounds();
                    bounds.extend(exploreMap.getCenter())
                    searchedOrgs = data;
                    markerManager.hide();
                    markerManagerSearch.clearMarkers()
                    markerManagerSearch.show()
                    //zoom level 0 3 for country
                    var markers = [];
                    jQuery.each(searchedOrgs['zoomed'],
                    function(i, val)
                    {
                        markers.push(createOrgMarkerWithCount(createItem(val)));
                        //image
                        if (exploreMap.getZoom() > 5)
                        {
                            bounds.extend(new GLatLng(val['item'][0][0], val['item'][0][1]));
                        }
                    });

                    map.setCenter(bounds.getCenter(), map.getBoundsZoomLevel(bounds))
                    markerManagerSearch.addMarkers(markers, 5);

                    markers.length = 0;
                    jQuery.each(searchedOrgs['countryLevel'],
                    function(i, val)
                    {
                        markers.push(markerCreator.createOrgMarkerWithCount(createItem(val)));
                    });
                    //all markers
                    markerManagerSearch.addMarkers(markers, 0, 5);
                    markerManagerSearch.refresh();
                });
            }
            else
            {
                var geocoder = new GClientGeocoder();
                geocoder.getLatLng(
                orgName,
                function(point) {
                    if (!point) {
                        //todo figure out what we do in this case
                        } else {
                        map.setCenter(point, 13);
                        var marker = new GMarker(point);
                        map.addOverlay(marker);
                        var htmlString = "<p>" + orgName + "</p>";
                        marker.openInfoWindowHtml(htmlString);
                        GEvent.addListener(marker, "infowindowclose",
                        function() {
                            exploreMap.removeOverlay(marker)
                        });
                    }
                }
                );

            }
        };
    this.handleBoundsChange = function() {
        var bounds = map.getBounds();
        for (countryCode in countriesInfo) {
            var countryInfo = countriesInfo[countryCode];
            var countryBounds = new GLatLngBounds(new GLatLng(countryInfo.bounds.southWest[0], countryInfo.bounds.southWest[1]), new GLatLng(countryInfo.bounds.northEast[0], countryInfo.bounds.northEast[1]));
            if (bounds.intersects(countryBounds)) {
                if (!countryInfo.hasStates
                && !countryInfo.loadedPostcodes
                && map.getZoom() > 4) {
                    jQuery.getJSON("/info/postcodes?countryCode=" + countryCode, processPostcodes);
                    jQuery.getJSON("/info/orgs?countryCode=" + countryCode, processOrgs);
                    countryInfo.loadedPostcodes = true;
                }
                if (countryInfo.hasStates
                && !countryInfo.loadedStates
                && map.getZoom() > 2) {
                    jQuery.getJSON("/info/states?countryCode=" + countryCode, processStates);
                    countryInfo.loadedStates = true;
                }
                if (countryInfo.hasStates
                && !countryInfo.loadedPostcodes
                && map.getZoom() > 4) {
                    jQuery.getJSON("/info/postcodes?countryCode=" + countryCode,processPostcodes);
                    jQuery.getJSON("/info/orgs?countryCode=" + countryCode, processOrgs);
                    countryInfo.loadedPostcodes = true;
                }
            }
        }
    };

    this.handleZoomChange = function() {
        if (map.getZoom() > 2 && map.getZoom() < 6 && !loadedCountries) {
            jQuery.getJSON("/info/countries", processCountries);
            loadedCountries = true;
        }
        if (map.getZoom() >= 0 && map.getZoom() < 4 && !loadedContinents) {
            jQuery.getJSON("/info/continents", processContinents);
            loadedContinents = true;
        }
    };
}


var MarkerCreator = function(map,ryv)
 {
    var util = new Util();
    var color = ryv ? "#0066cc" :"#ca6618";
    
    this.currentMarker = null;
    this.createOrgIcon = function(url) {
        var opts = {};
        opts.useImg = true;
        opts.image = url;
        opts.size = new GSize(32, 32);
        return opts;
    }

    this.createMedOrgIcon = function(url) {
        var opts = {}
        opts.useImg = true;
        opts.image = url;
        opts.size = new GSize(16, 16);
        return opts;
    }

    this.createSmallOrgIcon = function(url) {
        var opts = {}
        opts.useImg = true;
        opts.image = url;
        opts.size = new GSize(6, 6);
        return opts;
    }

    this.createBigIcon = function(label) {
        var iconOptions = {};
        iconOptions.size = new GSize(64, 26);
        iconOptions.backgroundColor = color;
        iconOptions.label = "" + label;
        return iconOptions;
    }

    this.createMediumIcon = function(label) {
        var iconOptions = {};
        iconOptions.size = new GSize(48, 22);
        iconOptions.backgroundColor = "#0097c4";
        iconOptions.label = "" + label;
        return iconOptions;
    }

    this.createSmallIcon = function(label) {
        var iconOptions = {};
        iconOptions.size = new GSize(24, 18);
        iconOptions.backgroundColor = "#85a20a";
        iconOptions.label = "" + label;
        return iconOptions;
    }

    this.createOrgMarkerWithCount = function(info) {
        if (info.icon.length == 0)
        {
            //default image for orgs with no image attached to them
            info.icon = 'http://www.google.com/intl/en_us/mapfiles/ms/micons/blue-dot.png';
        }
        if (!info.icon.match(/http/i))
        {
            info.icon = document.location.protocol + '//' +
            document.location.host + "/" + info.icon;
        }
        var marker = new MarkerLight(new GLatLng(info.center[0], info.center[1]), MarkerCreator.createOrgIcon(info.icon));
        GEvent.addListener(marker, "click",
        function() {
            map.openInfoWindowHtml(marker.getPoint(), "<b>" + info.name + "</b><br />Total Votes: " + info.count, {
                pixelOffset: new GSize(16, -16)
            });
        });
        return marker;
    }

    this.createOrgMarker = function(info) {
        var marker = new MarkerLight(new GLatLng(info.center[0], info.center[1]), this.createOrgIcon(info.icon));
        GEvent.addListener(marker, "click",
        function() {
            map.openInfoWindowHtml(marker.getPoint(), "<b>" + info.name + "</b>", {
                pixelOffset: new GSize(16, -16)
            });
        });
        return marker;
    }

    this.createMedOrgMarker = function(info) {
        var marker = new MarkerLight(new GLatLng(info.center[0], info.center[1]), this.createMedOrgIcon(info.icon));
        GEvent.addListener(marker, "click",
        function() {
            map.openInfoWindowHtml(marker.getPoint(), "<b>" + info.name + "</b>", {
                pixelOffset: new GSize(8, -8)
            });
        });
        return marker;
    }

    this.createSmallOrgMarker = function(info) {
        var marker = new MarkerLight(new GLatLng(info.center[0], info.center[1]), this.createSmallOrgIcon(info.icon));
        GEvent.addListener(marker, "click",
        function() {
            map.openInfoWindowHtml(marker.getPoint(), "<b>" + info.name + "</b>", {
                pixelOffset: new GSize(4, -4)
            });
        });
        return marker;
    }


    this.createMarker = function(markerType, locationCode, latlng, icon, title, zoom) {
        var voteLocation = util.getParameterByName("location");
        var infoWindowOptions = function() {
            var commentsWidth = 441;
            if (site_skin == "mini") {
                commentsWidth = 338;
            }
            return {
                maxTitle: title,
                maxContent: '\
     <div class="map_comments">\
       <div id="div-864264044956702366" style="width:' + commentsWidth + 'px;border:1px solid #cccccc;max-height:336px"></div>\
     </div>\
     '
            }
        }
        var marker = new MarkerLight(latlng, icon);
        marker.markerType = markerType;
        marker.locationCode = locationCode;
        marker.title = title;

        var tooltip = new MapTooltip(latlng, title, {
            offsetX: icon.size.width + 6
        });
        GEvent.addListener(marker, "mouseover",
        function() {
            map.addOverlay(tooltip);
        });
        GEvent.addListener(marker, "mouseout",
        function() {
            map.removeOverlay(tooltip);
        });
        if (markerType == 'continent')
        {
            GEvent.addListener(marker, "click",
            function() {
                map.openInfoWindowHtml(latlng,
                   '<p>' +  icon.label  +' people and organizations have shown their support for the COP15.</p><a href="#" id="showVote" onclick="VoteController.showVote();return false;">  Show your vote of support now.</a>',
                {
                    pixelOffset: new GSize(0, -icon.size.height)
                }
                );
            });

        }


        if (markerType != "continent") {
            var createInfoWindow = function() {
                currentMarker = marker;
                jQuery.getJSON("/info/votelocal?" + markerType + "=" + locationCode,
                function(gfcSigners) {
                    if (gfcSigners.length == 0) {
                        map.openInfoWindowHtml(latlng,
                        '<p>' +
                        icon.label + ' signed the petition here.' +
                        '</p>',
                        infoWindowOptions()
                        );
                        return;
                    }
                    var gfcIds = [];
                    for (var i = 0; i < gfcSigners.length; i++) {
                        gfcIds.push(gfcSigners[i]['gfcId']);
                    }
                    var params = {};
                    params[opensocial.DataRequest.PeopleRequestFields.PROFILE_DETAILS] = [opensocial.Person.Field.PROFILE_URL];
                    var openSocialReq = opensocial.newDataRequest();
                    var idSpec = opensocial.newIdSpec({
                        'userId': gfcIds
                    });
                    openSocialReq.add(openSocialReq.newFetchPeopleRequest(idSpec, params), 'signers');
                    openSocialReq.send(function(data) {
                        if (!data.hadError()) {
                            var signers = data.get('signers').getData();
                            var gfcImageList = '';
                            gfcImageList = gfcImageList + '<ul class="picture_set">';
                            signers.each(function(signer) {
                                if (signer.getField(opensocial.Person.Field.PROFILE_URL)) {
                                    gfcImageList = gfcImageList +
                                    '<li><a href="' +
                                    signer.getField(opensocial.Person.Field.PROFILE_URL) +
                                    '"><img src="' +
                                    signer.getField(opensocial.Person.Field.THUMBNAIL_URL) +
                                    '" alt="' + signer.getDisplayName() + '" /></a></li>';
                                } else {
                                    gfcImageList = gfcImageList +
                                    '<li><img src="' +
                                    signer.getField(opensocial.Person.Field.THUMBNAIL_URL) +
                                    '" alt="' + signer.getDisplayName() + '" /></li>';
                                }
                            });
                            gfcImageList = gfcImageList + '</ul>';
                            map.openInfoWindowHtml(latlng,
                            gfcImageList +
                            '<p>' +
                            icon.label + ' signed the petition here.' +
                            '</p>' +
                            '<p>' +
                            '<a href="javascript:exploreMap.getInfoWindow().maximize()">Discuss</a>' +
                            '</p>',
                            infoWindowOptions()
                            );
                        } else {
                            alert(data.getErrorMessage());
                        }
                    });
                });
            };
            GEvent.addListener(marker, "click", createInfoWindow);
            if (voteLocation == locationCode) {
                jQuery(window).load(function() {
                    // Open this marker immediately if this is where the voter is
                    // For the sake of GFC, needs to be in onload
                    createInfoWindow();
                });
            }
        }
        return marker;
    };
}


var Util = function()
 {
    this.getSiteBG = function(site_skin)
    {
        switch (site_skin) {
        case "mini":
            return "#fdf7eb"
            break;
        case "main":
        default:
            return "#f2f2f2";

        }
    }

    this.getParameterByName = function(name) {
        name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
        var regexS = "[\\?&]" + name + "=([^&#]*)";
        var regex = new RegExp(regexS);
        var results = regex.exec(window.location.href);
        if (results == null) {
            return "";
        } else {
            return results[1];
        }
    }
}
