//creating a Google API Map on the page
var geocoder1, map1;
function cal_map(address, id) {
    geocoder1 = new google.maps.Geocoder();
    geocoder1.geocode({
        'address': address
    }, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            var myOptions = {
                zoom: 14,
                center: results[0].geometry.location,
                mapTypeControl: false,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            }
            map1 = new google.maps.Map(document.getElementById("map-canvas-cal-" + id), myOptions);

            var marker = new google.maps.Marker({
                map: map1,
                position: results[0].geometry.location
            });
        }
    });
}

	var geocoder;
	var map;
	var infowindow = new google.maps.InfoWindow();
	var markers = [];

	function initialize() {
    	geocoder = new google.maps.Geocoder();
  		var latlng = new google.maps.LatLng(35.730885,-120.007383);
  		var mapOptions = {
			zoom: 6,
			mapTypeControl: false,
			streetViewControl: false,
			center: latlng,
			mapTypeId: 'roadmap'
	}

	if (document.getElementById('map-canvas') != null) {
  		map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

		// Create the search box and link it to the UI element.
		var input = document.getElementById('newslot_location');
		var searchBox = new google.maps.places.SearchBox(input);
	
		// Listen for the event fired when the user selects an item from the
		// pick list. Retrieve the matching places for that item.
		google.maps.event.addListener(searchBox, 'places_changed', function() {
			var places = searchBox.getPlaces();

			for (var i = 0, marker; marker = markers[i]; i++) {
				marker.setMap(null);
			}	

			// For each place, get the icon, place name, and location.
			markers = [];
			var bounds = new google.maps.LatLngBounds();
			for (var i = 0, place; place = places[i]; i++) {
				var image = {
					url: place.icon,
					size: new google.maps.Size(71, 71),
					origin: new google.maps.Point(0, 0),
					anchor: new google.maps.Point(17, 34),
					scaledSize: new google.maps.Size(25, 25)
				};

			 	// Create a marker for each place.
			 	var marker = new google.maps.Marker({
			  	  map: map,
			      icon: image,
			      title: place.name,
			      position: place.geometry.location
			    });

				markers.push(marker);
				bounds.extend(place.geometry.location);
			}
			map.fitBounds(bounds);
			map.setZoom(map.getZoom()-6);
		});

	// Bias the SearchBox results towards places that are within the bounds of the
	// current map's viewport.
		google.maps.event.addListener(map, 'bounds_changed', function() {
			var bounds = map.getBounds();
			searchBox.setBounds(bounds);
		});
	};
};