// Mapping of local stored values to human readable labels and styles
var LK_MAPPINGS = {
  '1': {
    label: 'Yay',
    color: '#00FF00'},
  '0': {
    label: 'Meh',
    color: 'orange'},
  '-1': {
    label: 'Nay',
    color: 'red'}
};

// Order of values in liker
var LK_LIST = ['1', '0', '-1'];

// Constants for data attributes used throughout
var LK_LIKEGROUP = 'data-likegroup';
var LK_LIKETYPE = 'data-liketype';
var LK_LIKEVALUE = 'data-likevalue';

// Create an interactive liker
function LK_createLiker(id) {
  var div = document.createElement('div');
  div.setAttribute(LK_LIKEGROUP, id);
  div.setAttribute(LK_LIKETYPE, 'full');
  for (var i = 0; i < LK_LIST.length; i++) {
    div.appendChild(LK_createLikerOption(id, LK_LIST[i]));
  }
  return div;
}

// Create option for each possible liker value
function LK_createLikerOption(id, value) {
  var span = document.createElement('span');
  span.setAttribute(LK_LIKEGROUP, id);
  span.setAttribute(LK_LIKEVALUE, value);
  span.innerHTML = LK_MAPPINGS[value].label;
  span.onclick = function() {
    LK_likeIt(span);
  };
  span.style.cursor = 'pointer';
  span.style.padding = '2px';
  span.style.borderRadius = '2px';
  LK_applyNormalStyle(span);
  if (localStorage[id] == value) {
    LK_applySelectedStyle(span, value);
  }
  return span;
}

// Create a read-only element that reflects like state
function LK_createLikerMini(id) {
  var span = document.createElement('span');
  span.setAttribute(LK_LIKEGROUP, id);
  span.setAttribute(LK_LIKETYPE, 'mini');
  span.style.borderRadius = '.3em';
  span.style.padding = '2px';
  var value = localStorage[id];
  if (value) {
    span.innerHTML = LK_MAPPINGS[value].label;
    LK_applySelectedStyle(span, value);
  } else {
    span.innerHTML = '';
  }
  return span;
}

// Function called when liker option is clicked
function LK_likeIt(elem) {
  var likeGroup = elem.getAttribute(LK_LIKEGROUP);
  var likeValue = elem.getAttribute(LK_LIKEVALUE);
  localStorage[likeGroup] = likeValue;

  // Change the style of the liker nodes
  var siblings = elem.parentNode.childNodes;
  for (var i = 0; i < siblings.length; i++) {
    if (siblings[i].style) { 
      LK_applyNormalStyle(siblings[i]);
    }
  }
  LK_applySelectedStyle(elem, likeValue);

  // Change the value of any mini likers
  var allSpans = document.getElementsByTagName('span');
  for (var i = 0; i < allSpans.length; i++) {
    var span = allSpans[i];
    if (span.getAttribute(LK_LIKEGROUP) == likeGroup) {
      if (span.getAttribute(LK_LIKETYPE) == 'mini') {
        span.innerHTML = LK_MAPPINGS[likeValue].label;
        LK_applySelectedStyle(allSpans[i], likeValue);
      }
    }
  }
}

// Reset liker option to normal style
function LK_applyNormalStyle(elem) {
  elem.style.fontWeight = 'normal';
  elem.style.backgroundColor = 'white';
}

// Change style to show this option is selected
function LK_applySelectedStyle(elem, value) {
  elem.style.fontWeight = 'bold';
  elem.style.backgroundColor = LK_MAPPINGS[value].color;
}
