function MapLightbox(map) {
  this.map = map;
  this.div = document.createElement('div');

  // hide
  this.div.style.visibility = 'hidden';

  // other style
  var height = parseInt(map.getContainer().style.height.split("px")[0]);
  var width = parseInt(map.getContainer().offsetWidth);

  this.div.style.width = width + "px";
  this.div.style.height = height + "px";
  this.div.style.padding = '0';
  this.div.style.border = 'none';
  this.div.style.backgroundColor = '#000000';
  this.div.style.zIndex = '100';
  this.div.style.opacity = '.55';
  this.div.style.filter = 'alpha(opacity=55)';

  var pos = new GControlPosition(G_ANCHOR_TOP_LEFT, new GSize(0, 0));
  pos.apply(this.div);
  map.getContainer().appendChild(this.div);
}

MapLightbox.prototype.show = function(html) {
  this.div.style.visibility = 'visible';
}

MapLightbox.prototype.close = function() {
  this.div.style.visibility = 'hidden';
}
