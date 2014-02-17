function tab_switch(new_tab, new_content, adjust_anchor) {
	adjust_anchor = adjust_anchor || false;
    document.getElementById('content-box-cal').style.display = 'none';
    document.getElementById('content-box-revs').style.display = 'none';
	document.getElementById('content-box-prop').style.display = 'none';
    //document.getElementById('content-box-rel').style.display = 'none';
    document.getElementById(new_content).style.display = 'block';
		if (adjust_anchor) {
		  document.location.hash = new_tab;
		}
		
		if (new_tab == "tab-prop" && typeof map != "undefined") {
			var center = map.getCenter();
			google.maps.event.trigger(map, "resize");
			map.setCenter(center);
		}

    document.getElementById('tab-cal').className = 'inactive';
    document.getElementById('tab-revs').className = 'inactive';
    document.getElementById('tab-prop').className = 'inactive';
    //document.getElementById('tab-rel').className = 'inactive';
	document.getElementById(new_tab).className = 'active'; 
}



function tab_switch_dash(new_tab, new_content) {
    document.getElementById('content-box-dprop').style.display = 'none';
    document.getElementById('content-box-dapps').style.display = 'none';
    document.getElementById(new_content).style.display = 'block';
  
    document.getElementById('tab-dprop').className = 'inactive';
    document.getElementById('tab-dapps').className = 'inactive';
    document.getElementById(new_tab).className = 'active'; 
}
