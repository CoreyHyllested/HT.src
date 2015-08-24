// GoogleMap API Wrapper.
var maps_version = 0.15;

var DEBUG = 1;
var infowindow;
var geocoder;
var markers;

$(document).ready(function () {
	console.log('maps.js: v' + maps_version);
	infowindow = new google.maps.InfoWindow();
	geocoder = new google.maps.Geocoder();
	markers = [];
	google_translate = {
		'room'			: '#addr_part_room',
		'floor'			: '#addr_part_floor',
		'street_number' : '#addr_part_number',
		'route'			: '#addr_part_route',

		'street_address'		: '#addr_street',
		'locality'				: '#addr_locale',
		'sublocality_level_1'	: '#addr_locale',
		'administrative_area_level_2'	: '#addr_aal2',
		'administrative_area_level_1'	: '#addr_aal1',
		'country'						: '#addr_aal0',

		'postal_code'		: '#addr_asst_postcode',
		'premise'			: '#addr_asst_premise',
		'colloquial_area'	: '#addr_asst_colloquial',
		'neighborhood'		: '#addr_asst_neighborhood',
		'intersection'		: '#addr_asst_intersection'
	}
});


/* Example invocation:
	init_canvas($('#map-canvas'), map_options, $('#project_addr'));
*/
function init_canvas(map_canvas, map_options, map_searchbox) {
	map_location = $(map_canvas).data('location');

	google.maps.event.addListener(map, 'bounds_changed', function() { map_bounds_changed(map, searchBox); });
	geocoder.geocode({'address': map_location}, function (results, status) {
		geocode_result_handler(results, status, map);
	});
}


function map_bounds_changed(map, searchBox) {
	searchBox.setBounds(map.getBounds());
}


function places_changed(map, search_input) {
	var places = search_input.getPlaces();
	if (places.length == 0)	return;

	for (var i = 0, marker; marker = markers[i]; i++) {
		marker.setMap(null);
	}
	markers = [];
	var bounds = new google.maps.LatLngBounds();

	// For each place: get icon, name, and location.
	for (var i = 0, place; place = places[i]; i++) {
		var image = {	url:		place.icon,
						size:		new google.maps.Size(71, 71),
						anchor:		new google.maps.Point(17, 34),
						origin:		new google.maps.Point(0, 0),
						scaledSize: new google.maps.Size(25, 25)
		};

		// Create a marker for each location.
		var marker = new google.maps.Marker({
						map:		map,
						icon:		image,
						title:		place.name,
						position:	place.geometry.location
		});

		markers.push(marker);
		bounds.extend(place.geometry.location);
	}
	map.fitBounds(bounds);
	map.setZoom(17);  // Why 17? Because it looks good.
}




function geocode_result_handler(result, status, map) {
	if (status == google.maps.GeocoderStatus.ZERO_RESULTS) {
	} else if (status == google.maps.GeocoderStatus.OVER_QUERY_LIMIT) {
	} else if (status == google.maps.GeocoderStatus.REQUEST_DENIED) {
	} else if (status == google.maps.GeocoderStatus.INVALID_REQUEST) {
	} else if (status == google.maps.GeocoderStatus.UNKNOWN_ERROR) {
	} else {
		if (DEBUG) { console.log('Geocoding success. ' + status); }
		map.fitBounds(result[0].geometry.viewport);
		if (DEBUG) { console.log(result[0].geometry.location_type.toLowerCase()); }
		if (DEBUG) { console.log(result[0].formatted_address); }
		if (DEBUG) { console.log(result[0].geometry.location); }
		var marker_title = result[0].formatted_address; // + ' at ' + latlng;
		marker = new google.maps.Marker({ position: result[0].geometry.location, title: marker_title, map: map });
		if (DEBUG) { console.log('marker_title = ' + marker_title); }
	}
}

function populate_address(results) {
	$('#addr_formatted').val(results.formatted_address);
	//results.place_id
	//results.geometry.location//lat,lng

	$.each(results.address_components, function (idx, address) {
		update = google_translate[address.types[0]];
		if (update) {
			$(update).val(address.short_name);
		} else {
			console.log('Missing element' + address.types);
		}
	});
}



function geocode_address(address) {
	var deferred = $.Deferred();
	address = $.trim(address)
	if (address === '') {
		deferred.resolve();
	}

	geocoder.geocode({'address': address }, function (results, status) {
		if (status == google.maps.GeocoderStatus.OK) {
			console.log('Geocoding success. ', results[0]);
			console.log(results[0].formatted_address);
			populate_address(results[0]);
			deferred.resolve();
		} else {
			deferred.reject();
		}
	});

	return deferred.promise();
	/*	potential error: google.maps.GeocoderStatus.ZERO_RESULTS
		also OVER_QUERY_LIMIT|REQUEST_DENIED|INVALID_REQUEST|UNKNOWN_ERROR
	*/
}


var mapOptions = {
	zoom: 10,
	mapTypeControl: false,
	streetViewControl: false,
	center: new google.maps.LatLng(40.0274, -105.2519),
	mapTypeId: google.maps.MapTypeId.ROADMAP
};
var default_options = mapOptions;



function initialize_map(canvas, searchinput) {
	initialize_map_dflt(canvas, searchinput, default_options);

	/*
	map_location = $('#' + canvas).data('location');
	if (map_location) {
		google.maps.event.addListener(map, 'bounds_changed', function() { map_bounds_changed(map, searchBox); });
		geocoder.geocode({'address': map_location}, function (results, status) {
				geocode_result_handler(results, status, map);
		});
	}
	*/
}


function initialize_map_dflt(name_canvas, name_search, options) {
	var markers = [];
	var elem_canvas = document.getElementById(name_canvas);
	var elem_search = document.getElementById(name_search);
	var map = new google.maps.Map(elem_canvas, options);

	// Create searchbox obj and link UI element to SearchBox obj.
	var searchBox = new google.maps.places.SearchBox(elem_search);

	// Listen for 'places_changed' event; user selected an item (place/location), retrieve place and update map
	google.maps.event.addListener(searchBox, 'places_changed', function() { places_changed(map, searchBox); });
}


