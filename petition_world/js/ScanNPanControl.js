function ScanNPanControl() {
}
ScanNPanControl.prototype = new GControl();

ScanNPanControl.prototype.initialize = function(map) {
    var container = document.createElement("div");
    container.innerHTML = '<a href="" id="stopScan" class="cop15_sprite" onclick="VOTEMAP.stopScan();return false;"></a><a href="" id="startScan" class="cop15_sprite" onclick="VOTEMAP.startScan();return false;"></a>';
    map.getContainer().appendChild(container);
    return container;
}

ScanNPanControl.prototype.getDefaultPosition = function() {
    return new GControlPosition(G_ANCHOR_TOP_RIGHT, new GSize(7,32));
}




function earthHourVote() {
}
earthHourVote.prototype = new GControl();

earthHourVote.prototype.initialize = function(map) {
       var container = document.createElement("div");
       container.innerHTML = '<a href="#" id="earthHour" class="earthHour" onclick="mapManager.showVoteControl();return false;"><img src="/images/ShowYourSupport.png"></img></a>';
       map.getContainer().appendChild(container);
       return container;
}

earthHourVote.prototype.getDefaultPosition = function() {
    return new GControlPosition(G_ANCHOR_BOTTOM_RIGHT, new GSize(5,20));
}


function earthHourVoteControl() {
}
earthHourVoteControl.prototype = new GControl();

earthHourVoteControl.prototype.initialize = function(map) {
       var container = document.createElement("div");
       var html = jQuery("#clone").html();
       html = html.replace(/remove/gi, '');
       container.innerHTML = html;
       map.getContainer().appendChild(container);
       return container;
}

earthHourVoteControl.prototype.getDefaultPosition = function() {
    return new GControlPosition(G_ANCHOR_BOTTOM_RIGHT, new GSize(0,0));
}


