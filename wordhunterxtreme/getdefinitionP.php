<?php 
require_once 'parser_php4.php';

$word = $_GET["word"];
$url 
= 
'http://services.aonaware.com/DictService/DictService.asmx/DefineInDict?dictId=wn&word='.$word;
$xml = file_get_contents($url);
//echo $xml;

$parser = new XMLParser($xml);
$parser->Parse();

if(count($parser->document->definitions[0]->definition[0]->worddefinition) > 0)
$definition = $parser->document->definitions[0]->definition[0]->worddefinition[0]->tagData;
$definition = str_replace("\n",",",trim($definition));
echo substr($definition, strlen($word)+2);
?>
