<?php
print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
 <ConfigMaps>
  <ConfigMap type=\"Skin\">
    <Meta name=\"title\">360cities: London</Meta>
    <Meta name=\"description\">Time-varying panoramas of London, taken by photographer Tom Mills. Visit 360cities.net for more panoramas across the globe.</Meta>
    <Meta name=\"author\">Tom Mills</Meta>
    <Meta name=\"author_email\">panoramas+themes@gmail.com</Meta>
    <Meta name=\"thumbnail\">http://imagine-it.org/google/themes/360cities_london_thumbnail.jpg</Meta>
    <Meta name=\"screenshot\">http://imagine-it.org/google/themes/360cities_london_screenshot.jpg</Meta>
  </ConfigMap>
";

$images = array(
"360cities_london_10pm_11pm.jpg",
"360cities_london_11am_12pm.jpg",
"360cities_london_11pm_12am.jpg",
"360cities_london_12am_3am.jpg",
"360cities_london_12pm_1pm.jpg",
"360cities_london_1pm_2pm.jpg",
"360cities_london_2pm_3pm.jpg",
"360cities_london_3am_6am.jpg",
"360cities_london_3pm_4pm.jpg",
"360cities_london_4pm_5pm.jpg",
"360cities_london_5pm_6pm.jpg",
"360cities_london_6am_7am.jpg",
"360cities_london_6pm_7pm.jpg",
"360cities_london_7am_8am.jpg",
"360cities_london_7pm_8pm.jpg",
"360cities_london_8am_9am.jpg",
"360cities_london_8pm_9pm.jpg",
"360cities_london_9am_10am.jpg",
"360cities_london_9pm_10pm.jpg"
);

foreach ($images as $image) {
  $arr = explode("_", $image);
  $from = $arr[2];
  $toA = explode(".", $arr[3]);
  $to = $toA[0];
  print "<ConfigMap type=\"Skin\">";
  print "<Trait name=\"TimeOfDay\">" . $from . "-" . $to . "</Trait>";
  print "<Attribute name=\"header.background_color\">#000000</Attribute>";
  print "<Attribute name=\"header.tile_image.url\">http://imagine-it.org/google/themes/" . $image . "</Attribute>";
  print "<Attribute name=\"header.center_image.url\">http://imagine-it.org/google/themes/" . $image . "</Attribute>";
  print "
    <Attribute name=\"header.link_color\">#ffffff</Attribute>
    <Attribute name=\"header.text_color\">#ffffff</Attribute>
    <Attribute name=\"header.logo\">beveled_white</Attribute>
    <Attribute name=\"footer.background_color\">#000000</Attribute>
    <Attribute name=\"footer.link_color\">#ffffff</Attribute>
    <Attribute name=\"footer.text_color\">#ffffff</Attribute>
    <Attribute name=\"attribution.image.url\">http://www.prague360.com/images/360cities-main.png</Attribute>
    <Attribute name=\"gadget_area.border_color\">#000000</Attribute>
    <Attribute name=\"gadget_area.gadget.border_color\">#000000</Attribute>
    <Attribute name=\"gadget_area.gadget.header.background_color\">#e6e6e6</Attribute>
    <Attribute name=\"gadget_area.gadget.header.text_color\">#000000</Attribute>
    <Attribute name=\"gadget_area.tab.border_color\">#ffffff</Attribute>
    <Attribute name=\"gadget_area.tab.selected.background_color\">#ffffff</Attribute>
    <Attribute name=\"gadget_area.tab.selected.text_color\">#ac142d</Attribute>
    <Attribute name=\"gadget_area.tab.unselected.background_color\">#ac142d</Attribute>
    <Attribute name=\"gadget_area.tab.unselected.text_color\">#ffffff</Attribute>
    <Attribute name=\"gadget_area.menu_icon.image.url\">http://igoogle-themes.googlecode.com/svn/trunk/000000_menu.gif</Attribute>
    <Attribute name=\"gadget_area.menu_icon.hover_image.url\">http://igoogle-themes.googlecode.com/svn/trunk/000000_menu_hover.gif</Attribute>
    <Attribute name=\"gadget_area.delete_icon.image.url\">http://igoogle-themes.googlecode.com/svn/trunk/000000_delete.gif</Attribute>
    <Attribute name=\"gadget_area.delete_icon.hover_image.url\">http://igoogle-themes.googlecode.com/svn/trunk/000000_delete_hover.gif</Attribute>
    <Attribute name=\"gadget_area.collapse_icon.image.url\">http://igoogle-themes.googlecode.com/svn/trunk/000000_collapse.gif</Attribute>
    <Attribute name=\"gadget_area.collapse_icon.hover_image.url\">http://igoogle-themes.googlecode.com/svn/trunk/000000_collapse_hover.gif</Attribute>
    <Attribute name=\"gadget_area.expand_icon.image.url\">http://igoogle-themes.googlecode.com/svn/trunk/000000_expand.gif</Attribute>
    <Attribute name=\"gadget_area.expand_icon.hover_image.url\">http://igoogle-themes.googlecode.com/svn/trunk/000000_expand_hover.gif</Attribute>
  </ConfigMap>";
}

print "</ConfigMaps>"
?>
