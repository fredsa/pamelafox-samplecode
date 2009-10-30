<?php
$order=1; // default to WordNet
$word = $_GET['word'];
$order = $_GET['order']; // 1=WordNet first, 2=UrbanDictionary first, 3=WordNet ONLY

echo $word;

// no results found anywhere
if( $order==1){ // default to WordNet
  $dict = "WordNet";
  $result = file_get_contents("http://imagine-it.org/google/getdefinitionP.php?word=".$word);
  $result = trim($result);
  if(strlen($result) < 6) { // no result in wordnet
    $dict = "UrbanDictionary";
    $result = file_get_contents("http://imagine-it.org/google/geturbandefinitionP.php?word=".$word);
    $result = trim($result);
  } 
  if(strlen($result) < 6) { // no result anywhere
     echo "\nno\n";
  } else {
     echo "\nyes\n".$result."\n".$dict;
  } 
}   
else if( $order==2){ // default to UD
  $dict = "UrbanDictionary";
  $result = file_get_contents("http://imagine-it.org/google/geturbandefinitionP.php?word=".$word);
  $result = trim($result);

  if(strlen($result) < 6) { // no result in wordnet
    $dict = "WordNet";
    $result = file_get_contents("http://imagine-it.org/google/getdefinitionP.php?word=".$word);
    $result = trim($result);
  } 
  if(strlen($result) < 6) { // no result anywhere
     echo "\nno\n";
  } else {
     echo "\nyes\n".$result."\n".$dict;
  } 
} else if ($order == 3) { // only use WordNET
  $dict = "WordNet";
  $result = file_get_contents("http://imagine-it.org/google/getdefinitionP.php?word=".$word);
  $result = trim($result);
  if(strlen($result) < 6) { // no result anywhere
     echo "\nno\n";
  } else {
     echo "\nyes\n".$result."\n".$dict;
  } 
} 
?>
