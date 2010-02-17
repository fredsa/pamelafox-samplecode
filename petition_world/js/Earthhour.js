
   var extraSubmitAction = function(userEmail,userPhone,userOptin)
    {w
        data = {};
        data.phone = userPhone;
        data.email = userEmail;
        data.optin = "0";
        if(userOptin == true)
        {
            data.optin = "1";
        }
        
        jQuery.ajax({url: "http://earthhour.staging.tigerspike.com/handlers/ExternalVote.ashx", data: data, type: "POST", cache: false, async: false});
    };
