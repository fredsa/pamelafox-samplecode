// google.load("jquery", "1.3.2");
// google.load("jqueryui", "1.7.2");
google.load("search", "1.0")
google.load("earth", "1");
google.load('friendconnect', '0.8');

// Needed for YouTube
window._uds_vbw_donotrepair = true;

var ge;
var currentTourKmlObject = null; // a KmlTour object
var currentFetchedKmlObject = null; // the original fetchKml'd target
var currentTourIndex = -1;
var currentExtraKmlsObject = null;
var loadingOverlay = null;

var appPath = document.location.protocol + '//' +
              document.location.host + document.location.pathname;

var visitorId = null;
var visitorName = null;

var locationId = "global";

var join_map;
var explore_map;

function learnReset() {
  // Destroy the existing plugin.
  // TODO(romannurik): assess the implications of this
  ge = null;
  jQuery('#map3d').html('');
  currentFetchedKmlObject = null;
  loadingOverlay = null;
}

/**
 * Init function called when the DOM is ready.
 */
function learnInit() {
  jQuery('#earth_container').show();
  if (!checkTourHash()) {
    // Timeout is required here, or the Earth plugin has problems.
    setTimeout(function() {
      learnReset();
      loadPlugin('earth', function() {
        if (loadingOverlay)
          loadingOverlay.setVisibility(false);
      });            
    }, 1);
  }

  // Generate the tour selection list.
  var tourListNode = jQuery('#learn #tourlist');
  // Clear the tour list
  tourListNode.html('');
  for (var i = 0; i < tourList.length; i++) {
    var tour = tourList[i];

    // Create the tour link and its container.
    var linkNode = jQuery(document.createElement('li'));
    linkNode.attr('id', 'tourind-' + i);

    // Handle clicks on the tour links.
    linkNode.click((function(tourIndex) {
      return function(e) {
        document.location.hash = '#' + tourList[tourIndex].id;
        loadTour(tourIndex);
      };
    })(i));

    var thumbnailNode = jQuery(document.createElement('img'));
    thumbnailNode.attr('src', tour.thumbnail);
    linkNode.append(thumbnailNode);

    var titleNode = jQuery(document.createElement('span'));
    titleNode.addClass('title');
    titleNode.html(tour.title);
    linkNode.append(titleNode);

    if (tour.duration) {
      var metaNode = jQuery(document.createElement('span'));
      metaNode.addClass('meta');
      metaNode.html('&nbsp;(' + tour.duration + ')');
      titleNode.append(metaNode);
    }

    if (tour.narrator) {
      var narratorNode = jQuery(document.createElement('span'));
      narratorNode.addClass('narrator');
      narratorNode.html('with ' + tour.narrator);
      linkNode.append(narratorNode);
    }

    tourListNode.append(linkNode);
  }

  // Hide the 'Loading' message and show the tourList list.
  jQuery('#tourlist_status').hide();
  jQuery('#tourlist_container').show();

  // Watch the document location hash for changes.
  window.setInterval(checkTourHash, 100);
}

/**
 * Check the document location hash/anchor and load the requested tour
 * if the anchor changes.
 * @return Returns true if the hash has changed and a new tour is loading, and
 *     false otherwise.
 */
function checkTourHash() {
  var destID = document.location.hash.match(/(\w+)/);
  if (destID)
    destID = destID[1];

  if (destID && (currentTourIndex < 0 ||
                 destID != tourList[currentTourIndex].id)) {

    // Find the tour with this ID.
    var destTourIndex = -1;
    for (var i = 0; i < tourList.length; i++) {
      if (tourList[i].id == destID) {
        destTourIndex = i;
        break;
      }
    }

    // Select the tour and open it up.
    if (destTourIndex >= 0) {
      loadTour(destTourIndex);
      return true;
    }
  }

  return false;
}

/**
 * Load the Google Earth Plugin instance, deleting any existing instance.
 * @param {string} mapType The planet type to load (either 'mars' or 'earth').
 */
function loadPlugin(mapType, callback) {
  google.earth.createInstance('map3d', function(pluginInstance) {
    // Earth Init Callback
    ge = pluginInstance;
    ge.getWindow().setVisibility(true);
    ge.getNavigationControl().setVisibility(ge.VISIBILITY_AUTO);

    // Create the loading overlay.
    var loadingImage = ge.createIcon('');
    loadingImage.setHref(appPath + 'images/loading.png');

    loadingOverlay = ge.createScreenOverlay('');
    loadingOverlay.setIcon(loadingImage);
    loadingOverlay.getOverlayXY().set(
        25, ge.UNITS_PIXELS, 25, ge.UNITS_INSET_PIXELS);
    loadingOverlay.getScreenXY().set(
        0, ge.UNITS_FRACTION, 1, ge.UNITS_FRACTION);
    loadingOverlay.getSize().set(-1, ge.UNITS_FRACTION, -1, ge.UNITS_FRACTION);
    ge.getFeatures().appendChild(loadingOverlay);

    // Load default view.
    var lookAt = ge.createLookAt('');
    lookAt.set(0.5, 0.5, 0, ge.ALTITUDE_RELATIVE_TO_GROUND,
        0, 0, 7000000);
    ge.getView().setAbstractView(lookAt);

    if (callback) {
      callback.call(null);
    }
  }, function(errorCode) {
    // Earth Failure Callback
    if (errorCode == 'ERR_NOT_INSTALLED' ||
        errorCode == 'ERR_CREATE_PLUGIN' && !google.earth.isInstalled()) {
      jQuery('#tourlist_status').html(
        'To tour the world in your browser, you must first install the ' +
        'Google Earth Plugin by clicking the download link to the right.'
      );
    } else {
      jQuery('#tourlist_status').addClass('error').html(
        'There was an error loading the touring application.'
      );
    }
  }, (mapType == 'mars' ?
         { database: 'http://khmdb.google.com/?db=mars' } : {}));
}

/**
 * Load the given tour and begin playback, stopping any currently playing tours.
 * Also selects the link to the tour and scrolls the link into view.
 */
function loadTour(tourIndex) {
  if (currentTourIndex == tourIndex)
    return;

  // Deselect the currently playing tour's link.
  var oldTourIndex = currentTourIndex;
  if (currentTourIndex >= 0) {
    document.getElementById('tourind-' + oldTourIndex).className = '';
    currentTourIndex = -1;
  }

  // Mark the link as selected and scroll it into view.
  var linkNode = document.getElementById('tourind-' + tourIndex);
  if (!linkNode)
    return;

  linkNode.className = 'selected';
  if ('linkNode' in linkNode)
    linkContainerNode.scrollIntoView(false);

  currentTourIndex = tourIndex;

  // Set up the embed link.
  resetEmbedLink(currentTourIndex);

  // Reload the plugin if necessary.
  if (!ge || oldTourIndex < 0 || tourList[currentTourIndex].mapType !=
                                 tourList[oldTourIndex].mapType) {
    learnReset();
    loadPlugin(tourList[currentTourIndex].mapType, continueLoadTour_);
  } else {
    if (loadingOverlay)
      loadingOverlay.setVisibility(true);

    continueLoadTour_(null);
  }
}

var overlays;
var captions;

/**
 * Continuation function for loadTour()
 */
function continueLoadTour_() {
  // Stop any currently playing tour.
  if (currentTourKmlObject) {
    //ge.getTourPlayer().reset();
    ge.getTourPlayer().setTour(null);
  }

  // Turn on/off extra layers.
  if (tourList[currentTourIndex].options) {
    ge.getLayerRoot().enableLayerById(ge.LAYER_BUILDINGS,
        tourList[currentTourIndex].options.buildings ? true : false);
  }

  // Load the first (or tourNumber'th) <gx:Tour> in the tour's KML URL.
  var tourNumber = tourList[currentTourIndex].tourNumber || 1;
  var tourIndexAtFetch = currentTourIndex;

  google.earth.fetchKml(
    ge,
    tourList[currentTourIndex].url,
    function(kmlObject) {
      if (!kmlObject) {
        // TODO(romannurik): non-obtrusive error.
        return;
      }

      // If the user clicks a different tour while this one is being fetched,
      // cancel the loading of this tour.
      if (tourIndexAtFetch != currentTourIndex) {
        return;
      }

      if (currentFetchedKmlObject) {
        ge.getFeatures().removeChild(currentFetchedKmlObject);
        currentFetchedKmlObject = null;
      }

      currentFetchedKmlObject = kmlObject;
      ge.getFeatures().appendChild(currentFetchedKmlObject);

      overlays = {};

      // Walk the loaded KML object hierarchy looking for a <gx:Tour>.
      walkKmlDom(kmlObject, function(context) {

        if (this.getType() == 'KmlScreenOverlay') {
          overlays[this.getId()] = this;
        }
        if (this.getType() == 'KmlTour' && !--tourNumber) {
          ge.getTourPlayer().setTour(this);

          // Hide the loading overlay.
          if (loadingOverlay)
            loadingOverlay.setVisibility(false);

          ge.getTourPlayer().play();

          currentTourKmlObject = this;
          //return false;
        }
      });

      // Remove any existing extra KMLs folder.
      if (currentExtraKmlsObject) {
        ge.getFeatures().removeChild(currentExtraKmlsObject);
        currentExtraKmlsObject = null;
      }

      loadCaptions(currentTourIndex);

      google.earth.addEventListener(ge, 'frameend', viewChanged);

      var tour = tourList[currentTourIndex];

      // Load any extra KML files necessary to view this tour into a new
      // folder.
      var extraKmls = tour.extraKmls || [];
      var currentExtraKmlsObject = ge.createFolder('');
      ge.getFeatures().appendChild(currentExtraKmlsObject);

      for (var i = 0; i < extraKmls.length; i++) {
        // Create a network link to this extra KML file
        // and place it in the extra KMLs folder.
        var link = ge.createLink('');
        link.setHref(extraKmls[i]);

        var networkLink = ge.createNetworkLink('');
        networkLink.setLink(link);

        currentExtraKmlsObject.getFeatures().appendChild(networkLink);
      }

      var footer_link = document.getElementById('footer_link');
      footer_link.href = tour.url;
      footer_link.innerHTML = "Open these layers and tour in Google Earth now!";
    }
  );
}

function loadCaptions(tourIndex) {
  $.getJSON('tours/captions' + tourIndex + '.js', captionsLoaded);
}

function captionsLoaded(json) {
  captions = json;
}


function viewChanged() {
  var caption = '';
  for (var id in captions) {
    var overlay = overlays[id];
    if (overlay.getVisibility()) {
      caption = captions[id];
    }
  }

  var oldCaption = $('#caption').html();
  if (oldCaption != caption) {
    $('#caption').html(caption);
  }
}

/**
 * Resets the 'embed this tour...' link to point to the Gadget wizard for
 * the tour at the given index in the tour list.
 */
function resetEmbedLink(tourIndex) {
  // Construct the embed link URL.
  var tourSpec = tourList[tourIndex];
  var tourOptions = tourSpec.options || {};

  var urlParams = {
    url: 'http://code.google.com/apis/kml/embed/tourgadget.xml',
    synd: 'open',
    title: tourSpec.title, // Gadgets apparently doesn't use this :(
    up_kml_url: tourSpec.url,
    up_tour_index: tourSpec.tourNumber || 1,
    up_show_navcontrols: 0,
    up_show_buildings: tourOptions.buildings ? 1 : 0,
    up_type_mars: (tourSpec.mapType == 'mars') ? 1 : 0
  };

  var urlParamArr = [];
  for (var key in urlParams) {
    urlParamArr.push(key + '=' + encodeURIComponent(urlParams[key]));
  }

  var baseUrl = 'http://www.gmodules.com/ig/creator';
  var embedUrl = baseUrl + '?' + urlParamArr.join('&');

  // Set the embed link properties.
  var embedSectionNode = document.getElementById('embedsection');
  if (embedSectionNode) {
    embedSectionNode.style.visibility = 'visible';
  }

  var embedLinkNode = document.getElementById('embedlink');
  if (embedLinkNode) {
    embedLinkNode.href = embedUrl;
  }
}

if (document.addEventListener) {
  document.addEventListener('DOMContentLoaded', cmxform, false);
}

function cmxform() {
  // Hide forms
  jQuery('form.cmxform').hide().end();

  // Processing
  jQuery('form.cmxform').find('li label').not('.nocmx').each(function(i) {
    var labelContent = this.innerHTML;
    var labelWidth = document.defaultView.getComputedStyle(this, '').getPropertyValue('width');
    var labelSpan = document.createElement('span');
    labelSpan.style.display = 'block';
    labelSpan.style.width = labelWidth;
    labelSpan.innerHTML = labelContent;
    this.style.display = '-moz-inline-box';
    this.innerHTML = null;
    this.appendChild(labelSpan);
  }).end();

  // Show forms
  jQuery('form.cmxform').show().end();
}

function loadVideoBar() {
  var videoBar;
  var options = {
    largeResultSet : !true,
    horizontal : true,
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
  jQuery('.org').hide();
  /* location of rpc_relay.html and canvas.html */
  google.friendconnect.container.setParentUrl('/gfc/');
  loadVideoBar();

  initJoinMap();
  initExploreMap();

  $('#show_your_vote').tabs().bind('tabsshow', function(event, ui) {
    switch (ui.index) {
    case 0:
      learnInit();
    case 1:
      learnReset();
      initJoinMap();
      if (geo_position_js.init()) {
        geo_position_js.getCurrentPosition(geoSuccess, geoError);
      } else {
        geoError();
      }
    case 2:
      learnReset();
      initExploreMap();
    }
  });
  
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
        } else {
          // Not logged in
          visitorId = null;
          visitorName = null;
        }
      });
    }
  });
  
  // jQuery('.loc').hide();
  populateCountries();
  learnInit();
});

function initJoinMap() {
  if (GBrowserIsCompatible()) {
    join_map = new GMap2(jQuery("#join_map")[0]);
    join_map.setCenter(new GLatLng(37.0625,-95.677068), 3);
    join_map.setUIToDefault();
  }
}

function initExploreMap() {
  if (GBrowserIsCompatible()) {
    explore_map = new GMap2(jQuery("#explore_map")[0]);
    explore_map.setCenter(new GLatLng(37.0625,-95.677068), 3);
    explore_map.setUIToDefault();
  }
}

function populateCountries() {
  jQuery('.state').hide();
  var countrySelect = jQuery('#country');
  countrySelect.change(populateStates);
  for (var countryCode in countriesInfo) {
    var countryOption = jQuery(document.createElement('option'));
    countryOption.val(countryCode);
    countryOption.text(countriesInfo[countryCode].name);
    countrySelect.append(countryOption);
  }
}

function populateStates() {
  var stateSelect = jQuery('#state');
  stateSelect.html('');
  var countryCode = jQuery('#country').val();
  var states = countriesInfo[countryCode].states;
  if (!states) {
    jQuery('.state').hide();
    return;
  }
  jQuery('.state').show();

  for (var i = 0; i < states.length; i++) {
    var stateOption = jQuery(document.createElement('option'));
    stateOption.val(states[i]);
    stateOption.text(states[i]);
    stateSelect.append(stateOption);
  }
}

function geoSuccess(p) {
  // We have a lat/lon point, do a reverse lookup
  var point = new GLatLng(p.coords.latitude, p.coords.longitude);
  var geocoder = new GClientGeocoder();
  geocoder.getLocations(point, addressHandler);
}

function addressHandler(response) {
  if (!response || response.Status.code != 200) {
    geoError();
  } else {
    var place = response.Placemark[0];
    var country = place.AddressDetails.Country.CountryNameCode;
    var state = place.AddressDetails.Country.AdministrativeArea.AdministrativeAreaName;
    // Sometimes Maps gives us an AdministrativeArea, and sometimes it gives a SubAdministrativeArea
    if (place.AddressDetails.Country.AdministrativeArea.Locality) {
      var city = place.AddressDetails.Country.AdministrativeArea.Locality.LocalityName;
      var postcode = place.AddressDetails.Country.AdministrativeArea.Locality.PostalCode.PostalCodeNumber;
    } else if (place.AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality) {
      var city = place.AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality.LocalityName;
      var postcode = place.AddressDetails.Country.AdministrativeArea.SubAdministrativeArea.Locality.PostalCode.PostalCodeNumber;
    } else {
      return geoError();
    }
    jQuery('#country').val(country).change();
    jQuery('#state').val(state);
    jQuery('#city').val(city);
    jQuery('#postcode').val(postcode);
    var geocoder = new GClientGeocoder();
    if (state) {
      geocoder.getLatLng(city + ", " + state + " " + postcode + ", " + country, latLngHandler);
    } else {
      geocoder.getLatLng(city + ", " + postcode + ", " + country, latLngHandler);
    }          
  }
}

function latLngHandler(point) {
  if (!point) {
    geoError();
  } else {
    if (!join_map) {
      initJoinMap();
    }
    join_map.setCenter(point, 13);
    var marker = new GMarker(point);
    join_map.addOverlay(marker);
  }
}

function geoError() {
  jQuery('.loc').show();
}

function toggleForm(formValue) {
  if (formValue == 'org') {
    jQuery('.person').hide();
    jQuery('.org').show();
  } else {
    jQuery('.org').hide();
    jQuery('.person').show();
  }
}
