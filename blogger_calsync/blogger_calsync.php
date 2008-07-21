<?php

require("account_info.php");
require("country_info.php");
require("blogger_calsync_common.php");

// This is the calendar we'll insert into
$calendarId = "2koofjh7qbucmnu3enn8galooc@group.calendar.google.com";

// This is the service we'll use to insert events into the calendar
$service = setupService($account_email, $account_password);

// Paginates through the blog feed, inserting each into the calendar feed
$has_next = true;
$request_url = "http://googlegeodevelopers.blogspot.com/feeds/posts/default";

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
    $where = "";
    $content = $it->content . " See original at ". $it->link[0]["href"];
    insertEvent($service, $calendarId, $title, $date, $where, $content);
  }
}

?>
