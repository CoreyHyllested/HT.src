$(document).ready(function () {
	console.log('about.js: ready');
	$('#masthead-text').css('opacity', '1');


	if(!(/Android|iPhone|iPad|iPod|BlackBerry|Windows Phone/i).test(navigator.userAgent || navigator.vendor || window.opera)){
		console.log('init skroller');
		var skrl = skrollr.init({
			//forceHeight: false,
			render:	function(data) {
				//Debugging - Log the current scroll position.
				//smoothScrolling: false;
				//console.log(data.curTop);
			},
		});
	}
});
