/**
* Returns an XMLHttp instance to use for asynchronous
* downloading. This method will never throw an exception, but will
* return NULL if the browser does not support XmlHttp for any reason.
* @return {XMLHttpRequest|Null}
*/
function createXmlHttpRequest() {
 try {
   if (typeof ActiveXObject != 'undefined') {
     return new ActiveXObject('Microsoft.XMLHTTP');
   } else if (window["XMLHttpRequest"]) {
     return new XMLHttpRequest();
   }
 } catch (e) {
   changeStatus(e);
 }
 return null;
};

/**
* This functions wraps XMLHttpRequest open/send function.
* It lets you specify a URL and will call the callback if
* it gets a status code of 200.
* @param {String} url The URL to retrieve
* @param {Function} callback The function to call once retrieved.
*/
function downloadUrl(url, type, data, callback) {
 var status = -1;
 var request = createXmlHttpRequest();
 if (!request) {
   return false;
 }

 request.onreadystatechange = function() {
   if (request.readyState == 4) {
     try {
       status = request.status;
     } catch (e) {
       // Usually indicates request timed out in FF.
     }
     callback(request.responseText, request.status);
     request.onreadystatechange = function() {};
   }
 }
 request.open(type, url, true);
 if (type == "POST") {
  request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  request.setRequestHeader("Content-length", data.length);
  request.setRequestHeader("Connection", "close"); 
 }

 try {
   request.send(data);
 } catch (e) {
   changeStatus(e);
 }
};

function downloadScript(url) {
  var script = document.createElement('script');
  script.src = url;
  document.body.appendChild(script);
}

/* This is the main program entry after the page loads completely. */
function highlightUser(me, div) {
	if (me == '') return;
    var meFinder = new RegExp('@' + me);
    var highlighting = {
    	'me': { 'backgroundColor': '#bedded', 'fontWeight': 'bold' }
	};

	var chatLines = div.childNodes;
	for(var a = 0; a < chatLines.length; a++) {
		var node = chatLines[a];
        if(node.tagName == 'DIV') {
          var result = meFinder.exec(node.innerHTML);
            if(result) {
              for(var cssStyle in highlighting.me) {
                node.style[cssStyle] = highlighting.me[cssStyle];
              }
            }
         }
     }
}


