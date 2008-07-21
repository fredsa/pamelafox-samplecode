<?php

ini_set("include_path", ".:/usr/lib/php:/usr/local/lib/php:../../../library/");
require_once 'Zend/Loader.php';
Zend_Loader::loadClass('Zend_Gdata');
Zend_Loader::loadClass('Zend_Gdata_ClientLogin');
Zend_Loader::loadClass('Zend_Gdata_Calendar');
Zend_Loader::loadClass('Zend_Http_Client');
Zend_Loader::loadClass('Zend_Gdata_App_Exception');

function setupService($email, $password) {
  $client = Zend_Gdata_ClientLogin::getHttpClient($email, $password,
          Zend_Gdata_Calendar::AUTH_SERVICE_NAME);
  $service = new Zend_Gdata_Calendar($client);
  return $service;
}

function insertEvent($service, $id, $title, $date, $where, $content) {
  // Create a new entry using the calendar service's magic factory method
  $event= $service->newEventEntry();

  // Populate the event with the desired information
  // Note that each attribute is crated as an instance of a matching class
  $event->title = $service->newTitle($title);
  $event->where = array($service->newWhere($where));
  $event->content = $service->newContent($content);

  $when = $service->newWhen();
  $when->startTime = $date;
  $when->endTime = $date;
  $event->when = array($when);

  // Upload the event to the calendar server
  // A copy of the event as it is recorded on the server is returned
  $newEvent = $service->insertEvent($event, "http://www.google.com/calendar/feeds/" . $id . "/private/full");
}

?>
