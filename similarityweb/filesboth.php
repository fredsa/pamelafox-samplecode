<?php

echo "<hr width='50%' color='#000000'/>";
echo "<br/>";
echo "<table>";
echo "<tr valign='top'>";
echo "<td valign='top' width='50%'>";
echo "<b><center>Newest webs:</center></b>";
include("files.php");
echo "</td>";
echo "<td valign='top'>";
echo "<b><center>Most viewed webs:</center><b>";
include("filespop.php");
echo "</td>";
echo "</tr></table>";

?>
