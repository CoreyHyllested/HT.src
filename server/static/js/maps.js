// Insprite's GoogleMap API Wrapper.

var DEBUG = 0;

if (DEBUG) { console.log('loading maps.js...'); }
var geocoder1;
var map1;
var infowindow = new google.maps.InfoWindow();
var geocoder = new google.maps.Geocoder();
var markers = [];


function cal_map(address, id) {
	if (DEBUG) { console.log('cal_map(' + address + ',' + id + ')\tenter'); }
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
			if (DEBUG) { console.log('cal_map(' + address + ',' + id + ')\t set map1'); }
            map1 = new google.maps.Map(document.getElementById("map-canvas-cal-" + id), myOptions);

            var marker = new google.maps.Marker({
                map: map1,
                position: results[0].geometry.location
            });
        }
    });
}


function initialize() {
	if (DEBUG) { console.log('initialize()\tdefine mapOptions'); }
	var mapOptions = {
		zoom: 6,
		mapTypeControl: false,
		streetViewControl: false,
		center: new google.maps.LatLng(35.730885,-120.007383),
		mapTypeId: 'roadmap'
	}

	if (DEBUG) { console.log('initialize()\tfind map-canvas'); }
	if (document.getElementById('map-canvas') != null) {
		if (DEBUG) { console.log('initialize()\tmap-canvas not null'); }
		map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

		// Create search box and link it to the UI element.
		if (DEBUG) { console.log('initialize()\tderp-derp.  Use prop_location'); }
		var input = document.getElementById('prop_location');
		var searchBox = new google.maps.places.SearchBox(input);
	
		// Listen for the event fired when the user selects an item from the
		// pick list. Retrieve the matching places for that item.
		if (DEBUG) { console.log('initialize()\tind map-canvas'); }
		google.maps.event.addListener(searchBox, 'places_changed', function() {
			if (DEBUG) { console.log('initialize()\tplaces_changed()\tenter'); }
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
				if (DEBUG) { console.log('initialize()\tplaces_changed()\tcreate marker' + i); }
				var marker = new google.maps.Marker({
				  map: map,
				  icon: image,
				  title: place.name,
				  position: place.geometry.location
				});

				if (DEBUG) { console.log('initialize()\tplaces_changed()\tpush marker'); }
				markers.push(marker);
				bounds.extend(place.geometry.location);
			}
			if (DEBUG) { console.log('initialize()\tplaces_changed()\'fitBounds + zoom'); }
			map.fitBounds(bounds);
			map.setZoom(map.getZoom()-6);
		});

		// Bias the SearchBox results towards places that are within the bounds of the current map's viewport.
		if (DEBUG) { console.log('initialize()\t addListener to \'bounds_changed\''); }
		google.maps.event.addListener(map, 'bounds_changed', function() {
			if (DEBUG) { console.log('initialize()\tbounds_changed() - get and set bounds'); }
			var bounds = map.getBounds();
			searchBox.setBounds(bounds);
		});
	};
}


function map_bounds_changed(map, searchBox) {
	if (DEBUG) { console.log('\t\tbounds_changed() - get and set bounds'); }
	var bounds = map.getBounds();
	if (searchBox != null) {
		searchBox.setBounds(bounds);
		if (DEBUG) { console.log('\t\tbounds_changed() - get bounds - ' + bounds); }
	}
}


function map_places_changed(map, searchBox) {
	if (DEBUG) { console.log('dash_canvas_initialize()\tplaces_changed()\tenter'); }
	var places = searchBox.getPlaces();

	for (var i = 0, marker; marker = markers[i]; i++) {
		marker.setMap(null);
	}	

	// For each place, get the icon, place name, and location.
	markers = [];
	var bounds = new google.maps.LatLngBounds();
	for (var i = 0, place; place = places[i]; i++) {
		if (DEBUG) { console.log('dash_canvas_initialize()\tplace\t' + place.name); }
		var image = {
			url: place.icon,
			size: new google.maps.Size(71, 71),
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(17, 34),
			scaledSize: new google.maps.Size(25, 25)
		};

		// Create a marker for each place.
		if (DEBUG) { console.log('dash_canvas_initialize()\tplaces_changed()\tcreate marker' + i); }
		var marker = new google.maps.Marker({
		  map: map,
		  icon: image,
		  title: place.name,
		  position: place.geometry.location
		});

		if (DEBUG) { console.log('dash_canvas_initialize()\tplaces_changed()\tpush marker'); }
		markers.push(marker);
		bounds.extend(place.geometry.location);
	}
	if (DEBUG) { console.log('dash_canvas_initialize()\tplaces_changed()\'fitBounds + zoom'); }
	map.fitBounds(bounds);
	map.setZoom(map.getZoom()-6);
}




function geocode_result_handler(result, status, map) {
	if (DEBUG) { console.log('right here' + result); }
	if (DEBUG) { console.log('right here' + status); }
	if (status == google.maps.GeocoderStatus.ZERO_RESULTS) {
		if (DEBUG) { console.log('Geocoding failed. zero results' + status); }
	} else if (status == google.maps.GeocoderStatus.OVER_QUERY_LIMIT) {
		if (DEBUG) { console.log('Geocoding failed. query limits' + status); }
	} else if (status == google.maps.GeocoderStatus.REQUEST_DENIED) {
		if (DEBUG) { console.log('Geocoding failed. req denied' + status); }
	} else if (status == google.maps.GeocoderStatus.INVALID_REQUEST) {
		if (DEBUG) { console.log('Geocoding failed. invalid' + status); }
	} else if (status == google.maps.GeocoderStatus.UNKNOWN_ERROR) {
		if (DEBUG) { console.log('Geocoding failed. unknown' + status); }
	} else {
		if (DEBUG) { console.log('Geocoding success. ' + status); }
		map.fitBounds(result[0].geometry.viewport);
		if (DEBUG) { console.log('1st result for geocoding is: ') }
		if (DEBUG) { console.log(result[0].geometry.location_type.toLowerCase()); }
		if (DEBUG) { console.log(result[0].formatted_address); }
		if (DEBUG) { console.log(result[0].geometry.location); }
		var marker_title = result[0].formatted_address; // + ' at ' + latlng;
		marker = new google.maps.Marker({ position: result[0].geometry.location, title: marker_title, map: map });

		if (DEBUG) { console.log('marker_title = ' + marker_title); }
	}
}


if (DEBUG) { console.log('maps.js\tdefine init_canvas()'); }
function init_canvas(map_canvas, map_options, map_searchbox) {
	map_id = $(map_canvas).data('uuid');
	map_location = $(map_canvas).data('location');

	if (DEBUG) { console.log('init_canvas()\t initialize canvas ('+map_id+')\t' + map_location); }
	if ($(map_canvas) != null) {
		if (DEBUG) { console.log('init_canvas()\tcanvas is not null'); }
		map_options.center = new google.maps.LatLng(39.968430, -105.153975);
		if (DEBUG) { console.log('init_canvas()\tpre\tmap_options.center = ', map_options.center); }

		var map = new google.maps.Map(map_canvas, map_options);
		if (DEBUG) { console.log('init_canvas()\tpst\tmap_options.center = ', map_options.center); }

		// create search box and link it to UI element.
		var searchBox = null;
		if (map_searchbox != null) {
			if (DEBUG) { console.log('init_canvas()\t.  Use map_searchbox, != null'); }
			searchBox = new google.maps.places.SearchBox(map_searchbox);

			// Listen for event fired when user selects an item from pick list. Retrieve the matching places for that item.
			if (DEBUG) { console.log('init_canvas()\t addListener to \'places_changed\' (drop-down picklist)'); }
			google.maps.event.addListener(searchBox, 'places_changed', function() { map_places_changed(map, searchBox); });
		}

		// Bias SearchBox results towards places that are within the bounds of the current map's viewport.
		if (DEBUG) { console.log('dash_canvas_initialize()\t addListener to \'bounds_changed\''); }
		google.maps.event.addListener(map, 'bounds_changed', function() { map_bounds_changed(map, searchBox); });

		geocoder.geocode({'address': map_location}, function (results, status) {
				if (DEBUG) { console.log('init_canvas()\tgeocode\tresults for ' + map_location); }
				geocode_result_handler(results, status, map);
		 });
	}
}


var mapOptions = {
	zoom: 6,
	mapTypeControl: false,
	streetViewControl: false,
	center: new google.maps.LatLng(35.730885,-120.007383),
	mapTypeId: 'roadmap'
}


function initialize_all_dashboard_maps() {
	$.each($('.scheduleMap'), function(idx, map) {
		if (DEBUG) { console.log('initialize_all_dashboard_maps()\t initialize canvas ('+idx+')'); }
		maps_search_input = null
		init_canvas(map, mapOptions, maps_search_input);
	});
}
