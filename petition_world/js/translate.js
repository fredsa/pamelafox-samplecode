$(document).ready(function() {
	var success = function(data, textStatus)
    {
    		for (el in data)
    		{
    			$("#"+el).val(data[el]);
    		}
    };
    
    var languageChange = function()
    {
    	
    	var arguments = {}
		arguments.languageCode = $(this).val();
  			$.ajax({
		  		url:'/info/translations',
		  		dataType: 'json',
		  		data: arguments,
		  		success: success
			});
	 };
	 $('#Language').change(languageChange);
});