    //globals, urgh, really need to port the entire application to run from mapmanager.js
    var campaigncode = "EH10";    
    var extraSubmitAction = function(userEmail,userPhone,userOptin,userName)
    {
        data = {};
        data.phone = userPhone;
        data.email = userEmail;
        data.optin = "0";
        data.name = userName;
        if(userOptin == true)
        {
            data.optin = "1";
        }
        jQuery.ajax({url: "http://www.earthhour.org/handlers/ExternalVote.ashx", data: data, type: "POST", cache: false, async: false});
    };
