<?php
include("awsI.php");
include("parser_php4.php");

$keyword = $_GET["keyword"];
$searchindex = $_GET["searchindex"];

$accesskey = '18SXRYH99ZRGNJXJRNG2';
//$asin =  '1590594762';
$url =  'http://webservices.amazon.com/onca/xml?Service=AWSECommerceService';
$url.=  "&AWSAccessKeyId=$accesskey";
// replace spaces with %20, figure out multiple search indexes
$url.=  "&Operation=ItemSearch&SearchIndex=$searchindex";
if($searchindex=="Magazines") $url.= "&Sort=subslot-salesrank";
else if($searchindex!="Blended") $url.= "&Sort=salesrank";

$url.=  '&ResponseGroup=Medium,OfferFull';
$keywordurl= $url."&Keywords=$keyword";

$toptitles = array("default","default","default","default","default");
$topranks = array(99999999,99999999,99999999,99999999,99999999);
$topasins = array(0,0,0,0,0);

$xml = file_get_contents($keywordurl);
$parser = new XMLParser($xml);
$parser->Parse();

foreach($parser->document->items[0]->item as $xml_item) {
  $title = $xml_item->itemattributes[0]->title[0]->tagData;
  $salesrank = $xml_item->salesrank[0]->tagData;
  $asin = $xml_item->asin[0]->tagData;
  for($j=0;$j<count($topranks);$j++) {
    if($salesrank < $topranks[$j] && $salesrank >= 1) {
      $topranks[$j] = $salesrank;
      $toptitles[$j] = $title;
      $topasins[$j] = $asin;
      $j=count($topranks);
    }
  }
}


print $keyword;
for($i=0;$i<count($topranks);$i++){
  if($topranks[$i] !=99999999){
    print "||".$toptitles[$i]. "**".$topranks[$i]."**".$topasins[$i];
  }
}
?>
