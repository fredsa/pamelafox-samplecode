<?php
//Capture data from $_POST array
$word = $_POST['word'];
$photoIds = array();
$servers = array();
$secrets = array();
$photoFreq = array();
$filename = "word_".$word.".txt";
//Open a file in write mode
$wholefile = file_get_contents($filename);
//parse it
//echo "photoIds=";
$entries = split("\n", $wholefile);

foreach($entries as $entry){
if(strlen($entry)>6){
$parts = split(" ",$entry);
array_push($photoIds, $parts[0]); 
}
}

$photoFreq = array_count_values($photoIds); 
//print_r($photoFreq); 
//echo "<br/>";
arsort($photoFreq); 
//print_r($photoFreq);
//echo "<br/>";
foreach($entries as $entry){
if(strlen($entry)>6){
$parts = split(" ",$entry);
$servers[($parts[0])] = $parts[1];
$secrets[($parts[0])] = $parts[2];
}
}
//echo "<br/>";
//print_r($servers);
//echo "<br/>";
//print_r($secrets);

$photoIdsString = "photoIds=";
$serversString = "&photoServers=";
$secretsString = "&photoSecrets=";
$uPhotoIds = array_unique($photoIds);
foreach($uPhotoIds as $photoId){
   $photoIdsString .= $photoId.",";
   $serversString .= $servers[$photoId].",";
   $secretsString .= $secrets[$photoId].",";
}
echo $photoIdsString.$serversString.$secretsString;

?>
