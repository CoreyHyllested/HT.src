$(document).ready(function () {
	console.log('about.js: ready');
	$('#masthead-text').css('opacity', '1');


	// Init Skrollr
	var skrl = skrollr.init({
		render:	function(data) {
			//Debugging - Log the current scroll position.
			console.log(data.curTop);
				}
	});

});
