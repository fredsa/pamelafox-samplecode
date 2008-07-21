<?php
include("awsI.php");
include("parser_php5.php");
include ("GraphViz.php");

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
//print "\n".$url;

$xml = file_get_contents($url);
$parser = new XMLParser($xml);
$parser->Parse();

if($parser->document->items[0]->request[0]->errors[0]->error[0]->code[0]->tagData == "AWS.ECommerceService.NoSimilarities"){
	print "Error\n";
}
else {
print "Success\n";
foreach($parser->document->items[0]->item as $xml_item){
	$ProductGroup = $xml_item->itemattributes[0]->productgroup[0]->tagData;
	$ASIN = $xml_item->asin[0]->tagData;

	$Title = $xml_item->itemattributes[0]->title[0]->tagData;
	$SalesRank = $xml_item->salesrank[0]->tagData;
	$SmallImage = $xml_item->smallimage[0]->url[0]->tagData;
	$MediumImage = $xml_item->mediumimage[0]->url[0]->tagData;
	$ListPrice = $xml_item->itemattributes[0]->listprice[0]->formattedprice[0]->tagData;
	$AverageRating = $xml_item->customerreviews[0]->averagerating[0]->tagData;
	$DetailPageURL = $xml_item->detailpageurl[0]->tagData;

	if(in_array($ASIN, $seenasins)){
		//print "already seen, not adding<br/>";
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

		// WRITE INFO TO DOT FILE
		//fwrite($fp, ("sim_".$ASIN." [label = \"".$Title."\"];\n"));
		//fwrite($fp, ("sim_".$ASIN." -> sim_".$aS.";\n"));
		
	}
	if($_GET['l'] == $l ){
		//print " at level 3<br/>";
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
//print $url;

$xml = file_get_contents($url);
$parser = new XMLParser($xml);
$parser->Parse();

foreach($parser->document->items[0]->item as $xml_item){
	$Title = $xml_item->itemattributes[0]->title[0]->tagData;
	$SalesRank = $xml_item->salesrank[0]->tagData;
	$SmallImage = $xml_item->smallimage[0]->url[0]->tagData;
	$MediumImage = $xml_item->mediumimage[0]->url[0]->tagData;
	$ListPrice = $xml_item->itemattributes[0]->listprice[0]->formattedprice[0]->tagData;
	$AverageRating = $xml_item->customerreviews[0]->averagerating[0]->tagData;
	$DetailPageURL = $xml_item->detailpageurl[0]->tagData;
}

// START DOT FILE
//$dotfn = "".$asinStart.".dotxt";
//$fp = fopen($dotfn, 'w') or die("Can't open dot file.");
//fwrite($fp, "digraph SIM {\n");


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
