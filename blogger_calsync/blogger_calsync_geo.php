<?php

require("account_info.php");
require("country_info.php");
require("blogger_calsync_common.php");

// This is the calendar we'll insert into
$calendarId = "2koofjh7qbucmnu3enn8galooc@group.calendar.google.com";

// This is the service we'll use to insert events into the calendar
$service = setupService($account_email, $account_password);

// Paginate through the blog feed, finding posts tagged with known country tags,
// and inserting them as events in the calendar feed.
$has_next = true;
$request_url = "http://googlemapsmania.blogspot.com/feeds/posts/default";
while ($has_next == true) { 
  $xml = simplexml_load_file($request_url) or die("feed not loading");
  $has_next = false;
  for ($i = 0; $i < count($xml->link); $i++) {
    $maybe_next_link = $xml->link[$i];
    if ($maybe_next_link['rel'] == "next") {
      $request_url = $maybe_next_link["href"];
      $has_next = true;
    }
  }

  foreach($xml->entry as $it) {
    $date = $it->published;
    $date = substr($date, 0, 10);
    $title = $it->title;
    $content = $it->content . " See original at ". $it->link[0]["href"];
    $num_countries = 0;
    foreach ($it->category as $ct) {
      $label  = $ct["term"];
      if (isset($countryInfo[(string)$label])) {
        $country = $label;
        $latlng = $countryInfo[(string)$label];
        $where = $country." @ ".$latlng;
        $num_countries++;
      }
    }
    if ($num_countries == 1) {
      insertEvent($service, $calendarId, $title, $date, $where, $content);
    }
  }
}

?>
