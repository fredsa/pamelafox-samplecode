// Search the text nodes for a US-style mailing address.
// Return null if none is found.
var blinkTags;
const browserAction = chrome.browserAction;

browserAction.onClicked.addListener(function() {
  chrome.tabs.getSelected(null, function(tab) {
    chrome.tabs.sendRequest(tab.id, {}, function(response) {
      // Do nothing
    });
  });
});

chrome.extension.onRequest.addListener(function(request, sender) {
   if (!sender.tab) return;
   var url = request.url;
   var xhr = new XMLHttpRequest();
   xhr.onreadystatechange = function() {
     if (xhr.readyState == 4) {
       var json = JSON.parse(xhr.responseText);
       if (json.status == 'success') {
         url = 'https://wave.google.com/a/wavesandbox.com/#minimized:search,restored:wave:' + json.wave_id.replace('+', '%252B');
         chrome.tabs.create({url: url});
       } else {
         alert('no worky');
       }
     }
   };
   xhr.open("GET", url, true);
   xhr.send();
 });