$(document).ready(function() {

	// On load, show full content on high resolutions
	if ($('.loginSwitch').css('display') == 'none') {
		$('.loginEmail').show();
		$('.loginSocial').show();
	}

	// On resize, show full content on high resolutions
	$(window).resize(function() {	
		if ($('.loginSwitch').css('display') == 'none') {
			$('.loginEmail').show();
			$('.loginSocial').show();
		}

		else if ($('.loginSwitch').css('display') !== 'none') {
			$('.loginEmail').show();
			$('.loginSocial').hide();
		}
	});


	// Switch to email login
	$('.loginSwitchEmail').click(function() {

		// If not highlighted, make it so
		if (!$(this).hasClass('loginSwitchActive')) {
			$(this).toggleClass('loginSwitchActive');
		}

		// Take away the highlight from the other tab
		if ($('.loginSwitchSocial').hasClass('loginSwitchActive')) {
			$('.loginSwitchSocial').toggleClass('loginSwitchActive');
		}

		// Hide the social login and show email login
		$('.loginSocial').hide();
		$('.loginEmail').show();	
	});


	// Switch to social login
	$('.loginSwitchSocial').click(function() {

		// If not highlighted, make it so
		if (!$(this).hasClass('loginSwitchActive')) {
			$(this).toggleClass('loginSwitchActive');
		}
		// Take away the highlight from the other tab
		if ($('.loginSwitchEmail').hasClass('loginSwitchActive')) {
			$('.loginSwitchEmail').toggleClass('loginSwitchActive');
		}

		// Hide the email login and show social login
		$('.loginEmail').hide();
		$('.loginSocial').show();

	});
});