// Search the text nodes for a US-style mailing address.
// Return null if none is found.
var blinkTags;

var findBlinkTags = function() {
  blinkTags = document.getElementsByTagName('blink');
  window.setInterval(makeTagsBlink, 500);
}

function makeTagsBlink() {  
  for (var i = 0; i < blinkTags.length; i++) {
    var blinkTag = blinkTags[i];
    var visibility = blinkTag.style.visibility;
    if (visibility == 'visible' || !visibility) {
      blinkTag.style.visibility = 'hidden';
    } else {
      blinkTag.style.visibility = 'visible';
    }
  } 
}

findBlinkTags();
