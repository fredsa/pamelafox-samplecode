<?php include("parser_php4.php");
$word = $_POST["word"];
$url 
= 
'http://services.aonaware.com/DictService/DictService.asmx/DefineInDict?dictId=wn&word='.$word;
$xml = file_get_contents($url);
$parser = new XMLParser($xml);
$parser->Parse();
$definition = 
$parser->document->definitions[0]->definition[0]->worddefinition[0]->tagData;
$splitdef = split(":",$definition);
echo substr($splitdef[1],1,50)."...";
?>
