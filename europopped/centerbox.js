window.CenterBox = function(mapDiv) {
  var mapWidth = mapDiv.offsetWidth;
  var mapHeight = mapDiv.offsetHeight;
  var boxWidth = 600;
  var boxHeight = Math.round(mapHeight * .80);
  var boxLeft = Math.round((mapWidth - boxWidth)/2) - 90;
  var boxTop = Math.round((mapHeight - boxHeight)/2);

  var centerDiv = document.createElement('div');
  centerDiv.style.padding = '5px';
  centerDiv.style.height = boxHeight + 'px';
  centerDiv.style.width = boxWidth + 'px';
  centerDiv.style.marginLeft = boxLeft + 'px';
  centerDiv.style.marginTop = boxTop + 'px';
  centerDiv.style.backgroundColor = 'white';
  centerDiv.style.border = '1px solid black';
  centerDiv.style.display = 'none';

  var topDiv = document.createElement('div');
  topDiv.style.height = '35px';
  var titleSpan = document.createElement('span');
  titleSpan.style.fontSize = '24px';
  titleSpan.style.fontWeight = 'bold';
  topDiv.appendChild(titleSpan);

  var closeImg = document.createElement('img');
  closeImg.style.float = 'right';
  closeImg.style.width = '32px';
  closeImg.style.height = '32px';
  closeImg.style.cursor = 'pointer';
  closeImg.style.marginTop = '0px';
  closeImg.src = 'http://gmaps-samples.googlecode.com/svn/trunk/images/closebigger.gif';
  topDiv.appendChild(closeImg);
  centerDiv.appendChild(topDiv);

  google.maps.event.addDomListener(closeImg, 'click', function() {
    centerDiv.style.display = 'none';
  });

  var sidebarDiv = document.createElement('div');
  sidebarDiv.style.float = 'right';
  sidebarDiv.style.marginRight = '7px';
  sidebarDiv.style.width = '200px';
  sidebarDiv.style.borderLeft = '2px solid black';
  sidebarDiv.style.paddingRight = '10px';
  sidebarDiv.style.height = (boxHeight - 35) + 'px';
  sidebarDiv.style.overflow = 'auto';
  sidebarDiv.innerHTML = 'Loading...';
  centerDiv.appendChild(sidebarDiv);

  var mainDiv = document.createElement('div');
  mainDiv.style.padding = '10px';
  mainDiv.style.height = (boxHeight - 35) + 'px';
  mainDiv.style.width = (boxWidth - 210) + 'px';
  mainDiv.style.textAlign = 'center';
  centerDiv.appendChild(mainDiv);

  this.div_ = centerDiv;
  this.titleSpan_ = titleSpan;
  this.sidebarDiv_ = sidebarDiv;
  this.mainDiv_ = mainDiv;
};

CenterBox.prototype.getDiv = function() {
  return this.div_;
}

CenterBox.prototype.setContent_ = function(div, content) {
  div.innerHTML = '';
  if (content instanceof Element) {
    div.appendChild(content);
  } else {
    div.innerHTML = content;
  }
}

CenterBox.prototype.setTitle = function(title) {
  this.setContent_(this.titleSpan_, title);
}

CenterBox.prototype.setSidebar = function(sidebar) {
  this.setContent_(this.sidebarDiv_, sidebar);
}

CenterBox.prototype.setMain = function(main) {
  this.setContent_(this.mainDiv_, main);
}

CenterBox.prototype.show = function() {
  this.div_.style.display = 'block';
}

CenterBox.prototype.hide = function() {
  this.div_.style.display = 'none';
}
