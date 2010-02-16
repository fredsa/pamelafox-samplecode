var extraSubmitAction = function(email,phone)
{
    alert('called');
    var data = {};
    data.email = email;
    data.phone = phone;
    data.optin = true;
    $.ajax({
      async: false,
    type: "GET",
    url: "http://earthhour.staging.tigerspike.com/handlers/externalvote.asmx/Vote?jsoncallback=?",
    data: data,
    contentType: "application/json; charset=utf-8",
    dataType: "jsonp",
    success: function(msg) {
      alert('hello world');
    },
    error: function(request, status, error)
    {
      debugger;
    }
  });
};