<?php
include("awsI.php");

$asinStart = $_GET['aS'];
$xmlfn = $asinStart.".xml";
$newasins = array();
$levels = array();
$seenlevels = array();
$seenasins = array();
$xmlnodes = array();
$numinlevel = 0;
$oldLevel = 0;

// START XML FILE
$doc = new DOMDocument('1.0', 'UTF-8');
$node = $doc->createElement("tree");
$parnode = $doc->appendChild($node);

function findSimilar(){
  global $newasins;
  global $levels;
  global $seenlevels;
  global $seenasins;
  global $xmlnodes;
  global $numinlevel;
  global $oldLevel;
  global $asinStart;
  global $asinEnd;
  global $fp;
  global $doc;

  $aS = array_shift($newasins);
  $l = array_shift($levels);
  $xnode = array_shift($xmlnodes);
  if($l != $oldLevel) $numinlevel=0;
  $oldLevel = $l;

  $accesskey = '18SXRYH99ZRGNJXJRNG2';
  $assoctag = 'amazonsimilar-20';
  $url =  'http://webservices.amazon.com/onca/xml?Service=AWSECommerceService';
  $url.=  "&AWSAccessKeyId=$accesskey&AssociateTag=$assoctag";
  $url.=  "&Operation=SimilarityLookup&ItemId=$aS";
  $url.=  '&ResponseGroup=Medium,Reviews';

  $xml = simplexml_load_file($url) or die("XML not loading");
  if ($xml->Items[0]->Request[0]->Errors[0]->Error[0]->Code[0] == "AWS.ECommerceService.NoSimilarities") {
    print "Error\n";
  } else { 
  print "Success\n";
  foreach($xml->Items[0]->Item as $xml_item){
    $ProductGroup = $xml_item->ItemAttributes[0]->ProductGroup[0];
    $ASIN = (string)$xml_item->ASIN[0];
    $Title = $xml_item->ItemAttributes[0]->Title[0];
    $SalesRank = $xml_item->SalesRank[0];
    $SmallImage = $xml_item->SmallImage[0]->URL[0];
    $MediumImage = $xml_item->MediumImage[0]->URL[0];
    $ListPrice = $xml_item->ItemAttributes[0]->ListPrice[0]->FormattedPrice[0];
    $AverageRating = $xml_item->CustomerReviews[0]->AverageRating[0];
    $DetailPageURL = $xml_item->DetailPageURL[0];
    if(in_array($ASIN, $seenasins)){
      print "already seen, not adding<br/>";
    } else {
      //print ($l." title ".$Title." product group ".$ProductGroup." asin ".$ASIN."<br/>");
      array_push($seenasins, $ASIN);
      array_push($seenlevels, ($l+1));
      array_push($newasins, $ASIN);	
      array_push($levels, ($l+1));

      // ADD TO XML DOCUMENT NODE      
      $node = $doc->createElement("Product");
      $newnode = $xnode->appendChild($node);

      $newnode->setAttribute("ASIN", $ASIN);
      $newnode->setAttribute("Title", $Title);
      $newnode->setAttribute("SalesRank", $SalesRank);
      $newnode->setAttribute("SmallImage", $SmallImage);
      $newnode->setAttribute("MediumImage", $MediumImage);
      $newnode->setAttribute("ListPrice", $ListPrice);
      $newnode->setAttribute("AverageRating", $AverageRating);
      $newnode->setAttribute("DetailPageURL", $DetailPageURL);

      // ADD XML NODE TO ARRAY
      array_push($xmlnodes, $newnode);
    }

    if($_GET['l'] == $l ){
      return;
    } 
  }
  findSimilar();
}

}

if (file_exists($xmlfn) ) {
  print "Results already found.";
  $content = file_get_contents($xmlfn);
  $fp = fopen("arbore.xml", 'w') or die("Can't open xml file.");
  fwrite($fp, $content);
  fclose($fp);
} else {
  // INITIALiZE ARRAYS WITH PARENT NODE
  array_push($newasins, $asinStart);
  array_push($seenasins, $asinStart);
  array_push($levels, 0);
  array_push($seenlevels, 0);

  // GET INFO ABOUT PARENT NODE
  $accesskey = '18SXRYH99ZRGNJXJRNG2';
  $url =  'http://webservices.amazon.com/onca/xml?Service=AWSECommerceService';
  $url.=  "&AWSAccessKeyId=$accesskey";
  $url.=  "&Operation=ItemLookup&ItemId=$asinStart";
  $url.=  '&ResponseGroup=Medium,Reviews';

  $xml = simplexml_load_file($url) or die("XML not loading");

  foreach($xml->Items[0]->Item as $xml_item){
    $Title = $xml_item->ItemAttributes[0]->Title[0];
    $SalesRank = $xml_item->SalesRank[0];
    $SmallImage = $xml_item->SmallImage[0]->URL[0];
    $MediumImage = $xml_item->MediumImage[0]->URL[0];
    $ListPrice = $xml_item->ItemAttributes[0]->ListPrice[0]->FormattedPrice[0];
    $AverageRating = $xml_item->CustomerReviews[0]->AverageRating[0];
    $DetailPageURL = $xml_item->DetailPageURL[0];
  }

  // WRITE PARENT NODE FOR XML FILE
  $node = $doc->createElement("Product");
  $newnode = $parnode->appendChild($node);
  $newnode->setAttribute("ASIN", $asinStart);
  $newnode->setAttribute("Title", $Title);
  $newnode->setAttribute("SalesRank", $SalesRank);
  $newnode->setAttribute("SmallImage", $SmallImage);
  $newnode->setAttribute("MediumImage", $MediumImage);
  $newnode->setAttribute("ListPrice", $ListPrice);
  $newnode->setAttribute("AverageRating", $AverageRating);
  $newnode->setAttribute("DetailPageURL", $DetailPageURL);

  array_push($xmlnodes, $newnode);

  findSimilar();

  if(count($newasins)>1){
    $xmlfile = $doc->saveXML();

  $xmlfn = $asinStart.".xml";
  $fp = fopen($xmlfn, 'w') or die("Can't open xml file.");
  fwrite($fp, $xmlfile);
  fclose($fp);

  $fp = fopen("arbore.xml", 'w') or die("Can't open arbore file.");
  fwrite($fp, $xmlfile);
  fclose($fp);
}

}

?>
