//creating a Google API Map on the page

console.log('maps.js\tenter');
var geocoder1;
var map1;
console.log('maps.js\tdefine infowindow');
var infowindow = new google.maps.InfoWindow();
var markers = [];
var geocoder = new google.maps.Geocoder();


console.log('maps.js\tdefine cal_map');
function cal_map(address, id) {
	console.log('cal_map(' + address + ',' + id + ')\tenter');
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
			console.log('cal_map(' + address + ',' + id + ')\t set map1');
            map1 = new google.maps.Map(document.getElementById("map-canvas-cal-" + id), myOptions);

            var marker = new google.maps.Marker({
                map: map1,
                position: results[0].geometry.location
            });
        }
    });
}

console.log('maps.js\tdefine initialize');
function initialize() {
	console.log('initialize() enter');

	console.log('initialize()\tdefine mapOptions');
	var mapOptions = {
		zoom: 6,
		mapTypeControl: false,
		streetViewControl: false,
		center: new google.maps.LatLng(35.730885,-120.007383),
		mapTypeId: 'roadmap'
	}

	console.log('initialize()\tfind map-canvas');
	if (document.getElementById('map-canvas') != null) {
		console.log('initialize()\tmap-canvas not null');
		map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

		// Create the search box and link it to the UI element.
		console.log('initialize()\tderp-derp.  Use newslot_location');
		var input = document.getElementById('newslot_location');
		var searchBox = new google.maps.places.SearchBox(input);
	
		// Listen for the event fired when the user selects an item from the
		// pick list. Retrieve the matching places for that item.
		console.log('initialize()\tind map-canvas');
		google.maps.event.addListener(searchBox, 'places_changed', function() {
			console.log('initialize()\tplaces_changed()\tenter');
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
				console.log('initialize()\tplaces_changed()\tcreate marker' + i);
				var marker = new google.maps.Marker({
				  map: map,
				  icon: image,
				  title: place.name,
				  position: place.geometry.location
				});

				console.log('initialize()\tplaces_changed()\tpush marker');
				markers.push(marker);
				bounds.extend(place.geometry.location);
			}
			console.log('initialize()\tplaces_changed()\'fitBounds + zoom');
			map.fitBounds(bounds);
			map.setZoom(map.getZoom()-6);
		});

		// Bias the SearchBox results towards places that are within the bounds of the current map's viewport.
		console.log('initialize()\t addListener to \'bounds_changed\'');
		google.maps.event.addListener(map, 'bounds_changed', function() {
			console.log('initialize()\tbounds_changed() - get and set bounds');
			var bounds = map.getBounds();
			searchBox.setBounds(bounds);
		});
	};
}


function map_bounds_changed(map, searchBox) {
	console.log('\t\tbounds_changed() - get and set bounds');
	var bounds = map.getBounds();
	if (searchBox != null) {
		searchBox.setBounds(bounds);
		console.log('\t\tbounds_changed() - get bounds - ' + bounds);
	}
}


function map_places_changed(map, searchBox) {
	console.log('dash_canvas_initialize()\tplaces_changed()\tenter');
	var places = searchBox.getPlaces();

	for (var i = 0, marker; marker = markers[i]; i++) {
		marker.setMap(null);
	}	

	// For each place, get the icon, place name, and location.
	markers = [];
	var bounds = new google.maps.LatLngBounds();
	for (var i = 0, place; place = places[i]; i++) {
		console.log('dash_canvas_initialize()\tplace\t' + place.name);
		var image = {
			url: place.icon,
			size: new google.maps.Size(71, 71),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(17, 34),
			scaledSize: new google.maps.Size(25, 25)
		};

		// Create a marker for each place.
		console.log('dash_canvas_initialize()\tplaces_changed()\tcreate marker' + i);
		var marker = new google.maps.Marker({
		  map: map,
		  icon: image,
		  title: place.name,
		  position: place.geometry.location
		});

		console.log('dash_canvas_initialize()\tplaces_changed()\tpush marker');
		markers.push(marker);
		bounds.extend(place.geometry.location);
	}
	console.log('dash_canvas_initialize()\tplaces_changed()\'fitBounds + zoom');
	map.fitBounds(bounds);
	map.setZoom(map.getZoom()-6);
}




function geocode_result_handler(result, status, map) {
	console.log('right here' + result);
	console.log('right here' + status);
	if (status == google.maps.GeocoderStatus.ZERO_RESULTS) {
		console.log('Geocoding failed. zero results' + status);
	} else if (status == google.maps.GeocoderStatus.OVER_QUERY_LIMIT) {
		console.log('Geocoding failed. query limits' + status);
	} else if (status == google.maps.GeocoderStatus.REQUEST_DENIED) {
		console.log('Geocoding failed. req denied' + status);
	} else if (status == google.maps.GeocoderStatus.INVALID_REQUEST) {
		console.log('Geocoding failed. invalid' + status);
	} else if (status == google.maps.GeocoderStatus.UNKNOWN_ERROR) {
		console.log('Geocoding failed. unknown' + status);
	} else {
		console.log('Geocoding success. ' + status);
		map.fitBounds(result[0].geometry.viewport);
		console.log('1st result for geocoding is: ')
		console.log(result[0].geometry.location_type.toLowerCase());
		console.log(result[0].formatted_address);
		console.log(result[0].geometry.location);
		var marker_title = result[0].formatted_address; // + ' at ' + latlng;
		marker = new google.maps.Marker({ position: result[0].geometry.location, title: marker_title, map: map });

		console.log('marker_title = ' + marker_title);
	}
}


console.log('maps.js\tdefine init_canvas()');
function init_canvas(map_canvas, map_options, map_searchbox) {
	map_id = $(map_canvas).data('uuid');
	map_location = $(map_canvas).data('location');

	console.log('init_canvas()\t initialize canvas ('+map_id+')\t' + map_location);
	if ($(map_canvas) != null) {
		console.log('init_canvas()\tcanvas is not null');
		map_options.center = new google.maps.LatLng(39.968430, -105.153975);
		console.log('init_canvas()\tpre\tmap_options.center = ', map_options.center);

		var map = new google.maps.Map(map_canvas, map_options);
		console.log('init_canvas()\tpst\tmap_options.center = ', map_options.center);

		// create search box and link it to UI element.
		var searchBox = null;
		if (map_searchbox != null) {
			console.log('init_canvas()\t.  Use map_searchbox, != null');
			searchBox = new google.maps.places.SearchBox(map_searchbox);

			// Listen for event fired when user selects an item from pick list. Retrieve the matching places for that item.
			console.log('init_canvas()\t addListener to \'places_changed\' (drop-down picklist)');
			google.maps.event.addListener(searchBox, 'places_changed', function() { map_places_changed(map, searchBox); });
		}

		// Bias SearchBox results towards places that are within the bounds of the current map's viewport.
		console.log('dash_canvas_initialize()\t addListener to \'bounds_changed\'');
		google.maps.event.addListener(map, 'bounds_changed', function() { map_bounds_changed(map, searchBox); });

		geocoder.geocode({'address': map_location}, function (results, status) {
				console.log('init_canvas()\tgeocode\tresults for ' + map_location);
				geocode_result_handler(results, status, map);
		 });
	}
}


console.log('maps.js()\tdefine mapOptions');
var mapOptions = {
	zoom: 6,
	mapTypeControl: false,
	streetViewControl: false,
	center: new google.maps.LatLng(35.730885,-120.007383),
	mapTypeId: 'roadmap'
}


console.log('maps.js\tdefine initialize_all_dashboard_maps()');
function initialize_all_dashboard_maps() {
	$.each($('.scheduleMap'), function(idx, map) {
		console.log('initialize_all_dashboard_maps()\t initialize canvas ('+idx+')');

		maps_search_input = null
		init_canvas(map, mapOptions, maps_search_input);
	});
}
