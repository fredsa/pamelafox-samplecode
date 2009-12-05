google.load("search", "1.0")
google.load("earth", "1");
google.load('friendconnect', '0.8');

var nonce;
var geocodeInProgress;
var visitorId = null;
var visitorName = null;
var locationId = "global";
var voteMap;
var toggler = 0;
var maxZoomSeen = 1;
var countries;
var orgs = {};
var searchedOrgs;
var loadedCountries = false;
var loadedContinents = false;
var markerManager;
var markerManagerSearch;



jQuery(document).ready(function() {
  initVoteMap();
  updateTwitter();
});

function initVoteMap() {
  voteMap = new GMap2(jQuery("#vote_map")[0]);
  //ensures this loads when the vote is submitted  
  var latlng = jQuery.cookie('latlng');
  if (latlng) {
    var point = new GLatLng(latlng.split(',')[0], latlng.split(',')[1]);
      voteMap.setCenter(point, 8);
  }
  else
  {
      voteMap.setCenter(new GLatLng(0,180), 1);
  }
  voteMap.setUIToDefault();
}

function updateTwitter()
{
    jQuery.getJSON('/info/twitter',function(data,status)
      {
    
            var twitterContainer = jQuery("#TwitterList");
            jQuery.each(data, function(i,tweet){
            if(i < 8)
            {
              twitterContainer.append("<li style='color:#F8EDD5'>"+tweet.name + "said: " + tweet.text +"</li>");
              if(tweet.geo)
              {
                //add to map
              }
          }
          });
    });
}