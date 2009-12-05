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


