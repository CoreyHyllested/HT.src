//switching tabs functionality for the profile page
function tab_switch(new_tab, new_content, adjust_anchor) {
	adjust_anchor = adjust_anchor || false;
    //set all tabs on the page to not visible
    document.getElementById('content-box-cal').style.display = 'none';
    document.getElementById('content-box-revs').style.display = 'none';
	document.getElementById('content-box-prop').style.display = 'none';

    //make only the new_content tab visible
    document.getElementById(new_content).style.display = 'block';
        //checking whether to load the page with a specific anchor
		if (adjust_anchor) {
		  document.location.hash = new_tab;
		}

        //checking if a map is involved in the reload of the tab
		if (new_tab == "tab-prop" && typeof map != "undefined") {
			var center = map.getCenter();
			google.maps.event.trigger(map, "resize");
			map.setCenter(center);
		}
    //mark all tabs on the page as inactive
    document.getElementById('tab-cal').className = 'inactive';
    document.getElementById('tab-revs').className = 'inactive';
    document.getElementById('tab-prop').className = 'inactive';
    //mark only the selected tab as active
	document.getElementById(new_tab).className = 'active'; 
}


//switching tabs functionality for the dashboard page
function tab_switch_dash(new_tab, new_content) {
    document.getElementById('content-box-dprop').style.display = 'none';
    document.getElementById('content-box-dapps').style.display = 'none';
    document.getElementById(new_content).style.display = 'block';
  
    document.getElementById('tab-dprop').className = 'inactive';
    document.getElementById('tab-dapps').className = 'inactive';
    document.getElementById(new_tab).className = 'active'; 
}
