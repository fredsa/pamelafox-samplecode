google.load("search", "1.0")
google.load('friendconnect', '0.8');

// Needed for YouTube
window._uds_vbw_donotrepair = true;

var appPath = document.location.protocol + '//' +
              document.location.host + document.location.pathname;

var exploreMap;
var markerManager;
var maxZoomSeen = 0;
var countries;
var loadedCountries = false;
var loadedContinents = false;
var locationId = "global";

function loadVideoBar() {
  var videoBar;
  var options = {
    largeResultSet : true,
    horizontal : true,
    thumbnailSize : GSvideoBar.THUMBNAILS_SMALL,
    autoExecuteList : {
      cycleTime : GSvideoBar.CYCLE_TIME_MEDIUM,
      cycleMode : GSvideoBar.CYCLE_MODE_LINEAR,
      executeList : ["ytchannel:cop15"]
    }
  }
  videoBar = new GSvideoBar(
    jQuery("#videoBar-bar")[0],
    GSvideoBar.PLAYER_ROOT_FLOATING,
    options
  );
}

jQuery(document).ready(function() {
  /* location of rpc_relay.html and canvas.html */
  google.friendconnect.container.setParentUrl('/gfc/');
  loadVideoBar();

  initExploreMap();

  google.friendconnect.container.initOpenSocialApi({
    site: '16982815293172380621',
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
});

function initExploreMap() {
  exploreMap = new GMap2(jQuery("#explore_map")[0]);
  exploreMap.setCenter(new GLatLng(37.0625,-95.677068), 3, G_PHYSICAL_MAP);
  exploreMap.setUIToDefault();
  var latlng = jQuery.cookie('latlng');
  if (latlng) {
    var point = new GLatLng(latlng.split(',')[0], latlng.split(',')[1]);
    exploreMap.setCenter(point, 8);
  }
  markerManager = new MarkerManager(exploreMap);
  GEvent.addListener(exploreMap, "zoomend", handleZoomChange);
  GEvent.addListener(exploreMap, "moveend", handleBoundsChange);
  handleZoomChange();
  handleBoundsChange();
}

function handleBoundsChange() {
  var bounds = exploreMap.getBounds();
  for (countryCode in countriesInfo) {
    var countryInfo = countriesInfo[countryCode];
    var countryBounds = new GLatLngBounds(new GLatLng(countryInfo.bounds.southWest[0], countryInfo.bounds.southWest[1]), new GLatLng(countryInfo.bounds.northEast[0], countryInfo.bounds.northEast[1]));
    if (bounds.intersects(countryBounds)) {
      if (!countryInfo.hasStates
       && !countryInfo.loadedPostcodes
       && exploreMap.getZoom() > 4) {
        jQuery.getJSON("/info/postcodes?countryCode=" + countryCode, processPostcodes);
        countryInfo.loadedPostcodes = true;
      }
      if ( countryInfo.hasStates
       && !countryInfo.loadedStates
       && exploreMap.getZoom() > 2) {
        jQuery.getJSON("/info/states?countryCode=" + countryCode, processStates);
        countryInfo.loadedStates = true;
      }
      if ( countryInfo.hasStates
       && !countryInfo.loadedPostcodes
       && exploreMap.getZoom() > 4) {
        jQuery.getJSON("/info/postcodes?countryCode=" + countryCode, processPostcodes);
        countryInfo.loadedPostcodes = true;
      }
    }
  }
}

function handleZoomChange() {    
 if (exploreMap.getZoom() > 2 && exploreMap.getZoom() < 6 && !loadedCountries) {
   jQuery.getJSON("/info/countries", processCountries);
   loadedCountries = true;
 }
 if (exploreMap.getZoom() >= 0 && exploreMap.getZoom() < 4 && !loadedContinents) {
   jQuery.getJSON("/info/continents", processContinents);
   loadedContinents = true;
 }
}

function processContinents(json) {
  var info = json;
  var markers = [];
  for (continentCode in info.continents) {
    var continent = info.continents[continentCode];
    if (continent.count == 0) continue;
    var marker = createMarker("continent", continentCode, new GLatLng(continent.center[0], continent.center[1]), createBigIcon(continent.count), continent.name, 3);
    markers.push(marker);
  }
  markerManager.addMarkers(markers, 0, 2);
  markerManager.refresh();
}

function processCountries(json) {
  var info = json;
  var markers = [];
  for (countryCode in info.countries) {
    var country = info.countries[countryCode];
    var marker = createMarker("country", countryCode, new GLatLng(country.center[0], country.center[1]), createBigIcon(country.count), country.name, 6);
    markers.push(marker);
  }
  markerManager.addMarkers(markers, 3, 5);
  markerManager.refresh();
}

function processStates(json) {
  var info = json;
  var markers = [];
  for (stateCode in info.states) {
    var state = info.states[stateCode];
    var marker = createMarker("state", stateCode, new GLatLng(state.center[0], state.center[1]), createMediumIcon(state.count), state.name, 6);
    markers.push(marker);
  }

  markerManager.addMarkers(markers, 3, 5);
  markerManager.refresh();
}

function processPostcodes(json) {
  var info = json;
  var markers = [];
  for (postcodeCode in info.postcodes) {
    var postcode = info.postcodes[postcodeCode];
    var marker = createMarker("postcode", postcodeCode, new GLatLng(postcode.center[0], postcode.center[1]), createSmallIcon(postcode.count), postcodeCode, 14);
    markers.push(marker);
  }

  markerManager.addMarkers(markers, 6);
  markerManager.refresh();
}

function createBigIcon(label) {
  var iconOptions = {};
  iconOptions.width = 32;
  iconOptions.height = 32;
  iconOptions.primaryColor = "#b3e742";
  iconOptions.label = "" + label;
  iconOptions.labelSize = 20;
  iconOptions.labelColor = "#FFFFFF";
  iconOptions.shape = "roundrect";
  var icon = MapIconMaker.createFlatIcon(iconOptions);
  icon.iconOptions = iconOptions;
  return icon;
}

function createMediumIcon(label) {
  var iconOptions = {};
  iconOptions.width = 24;
  iconOptions.height = 24;
  iconOptions.primaryColor =  "#86cb23";
  iconOptions.label = "" + label;
  iconOptions.labelSize = 16;
  iconOptions.labelColor = "#FFFFFF";
  iconOptions.shape = "roundrect";
  var icon = MapIconMaker.createFlatIcon(iconOptions);
  icon.iconOptions = iconOptions;
  return icon;
}

function createSmallIcon(label) {
  var iconOptions = {};
  iconOptions.width = 18;
  iconOptions.height = 18;
  iconOptions.primaryColor = "#5fa612";
  iconOptions.label = "" + label;
  iconOptions.labelSize = 12;
  iconOptions.labelColor = "#FFFFFF";
  iconOptions.shape = "roundrect";
  var icon = MapIconMaker.createFlatIcon(iconOptions);
  icon.iconOptions = iconOptions;
  return icon;
}

function createMarker(markerType, locationCode, latlng, icon, title, zoom) {
  var marker = new GMarker(latlng, {icon: icon});
  var tooltip = new MapTooltip(marker, title, {offsetX: icon.iconOptions.width - 6, backgroundColor: icon.iconOptions.primaryColor});
  GEvent.addListener(marker, "mouseover", function() {
    exploreMap.addOverlay(tooltip);
  });
  GEvent.addListener(marker, "mouseout", function() {
    exploreMap.removeOverlay(tooltip);
  });
  if (markerType != "continent") {
    GEvent.addListener(marker, "click", function() {
      jQuery.getJSON("/info/votelocal?" + markerType + "=" + locationCode, function (gfcSigners) {
        var gfcIds = [];
        for (var i = 0; i < gfcSigners.length; i++) {
          gfcIds.push(gfcSigners[i]['gfcId']);
        }
        var openSocialReq = opensocial.newDataRequest();
        var idSpec = opensocial.newIdSpec({'userId': gfcIds});
        openSocialReq.add(openSocialReq.newFetchPeopleRequest(idSpec), 'signers');
        openSocialReq.send(function (data) {
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
            marker.openInfoWindowHtml(
              gfcImageList +
              '<p>' +
                icon.iconOptions.label + ' signed the petition here.' +
              '</p>'
            );
          } else {
            alert(data.getErrorMessage());
          }
        });
      });
    });
  }
  return marker;
}

