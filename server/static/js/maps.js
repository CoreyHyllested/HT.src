// GoogleMap API Wrapper.
var maps_version = 0.8;

var DEBUG = 1;
var infowindow;
var geocoder;
var markers;

$(document).ready(function () {
	console.log('maps.js: v' + maps_version);
	infowindow = new google.maps.InfoWindow();
	geocoder = new google.maps.Geocoder();
	markers = [];
});


/* Example invocation:
	init_canvas($('#map-canvas'), map_options, $('#project_addr'));
*/
function init_canvas(map_canvas, map_options, map_searchbox) {
	map_location = $(map_canvas).data('location');

	if ($(map_canvas) != null) {
		var map = new google.maps.Map(map_canvas, map_options);
		var searchBox = null;
		if (map_searchbox != null) {
			searchBox = new google.maps.places.SearchBox(map_searchbox);
			google.maps.event.addListener(searchBox, 'places_changed', function() { places_changed(map, searchBox); });
		}

		google.maps.event.addListener(map, 'bounds_changed', function() { map_bounds_changed(map, searchBox); });
		geocoder.geocode({'address': map_location}, function (results, status) {
				geocode_result_handler(results, status, map);
		});
	}
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


