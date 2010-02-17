$(document).ready(function()
{
	var width = $("#MapTop").width();
	if($("#vote_map").length > 0)
	{
		//40 is the padding and margin allowance
		width += $("#vote").width() +140;
		if(width < 892)
		 	width = 892;
	}
	$("#show_your_vote").width(width);
});