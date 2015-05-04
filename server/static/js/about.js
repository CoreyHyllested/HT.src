$(document).ready(function () {
	console.log('about.js: ready');
	$('#masthead-text').css('opacity', '1');


	// Init Skrollr
	var skrl = skrollr.init({
		render:	function(data) {
			//Debugging - Log the current scroll position.
			//smoothScrolling: false;
			//console.log(data.curTop);
			}
	});

});
