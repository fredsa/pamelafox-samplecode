    //globals, urgh, really need to port the entire application to run from mapmanager.js
    var campaigncode = "EH10";    
    var extraSubmitAction = function(userEmail,userPhone,userOptin,name)
    {
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
