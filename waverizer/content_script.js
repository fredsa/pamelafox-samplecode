chrome.extension.onRequest.addListener(function(request) {
   var selection = window.getSelection();
   var address = 'pamela.fox@wavesandbox.com';
   var url = 'http://waverizer.appspot.com/web/create';
   url += '?note=' + escape(selection);
   url += '&url=' + window.location.href;
   url += '&address=' + address;
   chrome.extension.sendRequest({url: url});
   console.log('sent url: ' + url);
});
