<?php
require_once("parser_php4.php");

$recentfiletimes = array(1148685152,1148685152,1148685152,1148685152,1148685152);
$recentfilenames = array("default","default","default","default","default");
$files = array();

if ($handle = opendir('.')) {

  while (false !== ($file = readdir($handle))) {
    $ext = substr(strrchr($file, "."), 1);
    if ($file != "." && $file != ".." && $file != "arbore.xml" && $file != "games.xml" && $ext == "xml") {
      $filetime = filemtime($file);
      $key = $filetime.$file;
      $files[$key] = $file;
    }
  }
  closedir($handle);
}

ksort($files);
$files = array_reverse($files);

$i=0;
echo "<UL>";
foreach($files as $file){
  $xml = file_get_contents($file);
  $parser = new XMLParser($xml);
  $parser->Parse();
  $product = $parser->document->product[0];
  $title =  $product->tagAttrs['title'];

  echo "<LI><a href=\"arbore.php?XMLFileName=".$file."\" target=\"new\">".$title."</a></LI>";
  echo "<br/>";

  $i++;
  if($i==7) break;
}
echo "</UL>";

?>
