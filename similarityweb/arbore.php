<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
<title>Similarity Web</title>
</head>
<body bgcolor="#ffffff">
<!--url's used in the movie-->
<!--text used in the movie-->
<!--
<p align="left"><font face="Arial" size="11" color="#000000" letterSpacing="0.000000" kerning="0"><b>Structure of tree:</b></font></p>
Vizualizare grafica
Roll over a product for more information...
-->
<!-- saved from url=(0013)about:internet -->
<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,0,0" width="950" height="650" id="arbore_genealogic2" align="middle">
<?php
$XMLFileName = $_GET['XMLFileName'];
if($XMLFileName==""){ $XMLFileName = "arbore.xml"; }
?>
<PARAM NAME=FlashVars VALUE="XMLFileName=
<?php print $XMLFileName; ?> 
"/>
<param name="allowScriptAccess" value="sameDomain" />
<param name="movie" value="arbore_genealogic.swf" />
<param name="quality" value="high" />
<param name="bgcolor" value="#ffffff" />
<embed FlashVars="XMLFileName=
<?php print $XMLFileName; ?>
" src="arbore_genealogic2.swf" quality="high" bgcolor="#ffffff" width="950" height="650" name="arbore_genealogic2" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" />
</object>
<?php
// find file with this name
// if doesnt exist create with counter 1
// if exists rename, inc counter
// format #_ASIN
// We do this to keep track of view counts so we know most popular files
if($XMLFileName!="arbore.xml"){
  $asinL = substr($XMLFileName, 0, strpos($XMLFileName,"."));

  $found = false;

  if ($handle = opendir('cnt/')) {
    while (false !== ($file = readdir($handle))) {
      $asinT = substr($file, strpos($file,"_")+1);
      $asinT = substr($asinT, 0, strpos($asinT,"."));
      if ($asinT == $asinL) {
        $counter = substr($file, 0,  strpos($file,"_")+1);
        $counterN = intval($counter)+1;
        $found = true;
        $fileNew = $counterN."_".$asinT.".txt";
        rename("cnt/".$file, "cnt/".$fileNew);
        break;
     }
  }
  closedir($handle);
}

if(!$found) {
  $fileNew = "cnt/1_".$asinL.".txt";
  $fh = fopen($fileNew,"w");
  fclose($fh);
  }
}
?>
</body>
</html>
