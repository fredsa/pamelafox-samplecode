<?php


require_once("parser_php4.php");

$filess = array();

if ($handle = opendir('cnt/')) {
while (false !== ($fileYo = readdir($handle))) {
$ext = substr(strrchr($fileYo, "."), 1);
if ($fileYo != "." && $fileYo != ".." && $ext == "txt") {
$key = substr($fileYo, 0,  strpos($fileYo,"_")+1).$fileYo;
$filess[$key]=$fileYo;

}
}
closedir($handle);
}

ksort($filess, SORT_NUMERIC);

$filess = array_reverse($filess);

$i=0;
echo "<UL>";
foreach($filess as $fileYo){
$asinT = substr($fileYo, strpos($fileYo,"_")+1);
$asinT = substr($asinT, 0, strpos($asinT,"."));

$fileN = "./".$asinT.".xml";
$fileNN = $asinT.".xml";
$xml = file_get_contents($fileN);
$parser = new XMLParser($xml);
$parser->Parse();
$product = $parser->document->product[0];

$title =  $product->tagAttrs['title'];

echo "<LI><a href=\"arbore.php?XMLFileName=".$fileNN."\" target=\"new\">".$title."</a></LI>";
echo "<br/>";

$i++;
if($i==7) break;
}
echo "</UL>";



?>