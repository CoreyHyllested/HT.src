$(document).ready(function() {
	// Switch to email signup
	$('.signupSwitchEmail').click(function() {

		// If not highlighted, make it so
		if (!$(this).hasClass('signupSwitchActive')) {
			$(this).toggleClass('signupSwitchActive');
		}

		// Take away the highlight from the other tab
		if ($('.signupSwitchSocial').hasClass('signupSwitchActive')) {
			$('.signupSwitchSocial').toggleClass('signupSwitchActive');
		}

		// Hide the social signup and show email signup
		$('.signupSocial').hide();
		$('.signupEmail').show();
				
	});


	// Switch to social signup
	$('.signupSwitchSocial').click(function() {

		// If not highlighted, make it so
		if (!$(this).hasClass('signupwitchActive')) {
			$(this).toggleClass('signupSwitchActive');
		}
		// Take away the highlight from the other tab
		if ($('.signupSwitchEmail').hasClass('signupSwitchActive')) {
			$('.signupSwitchEmail').toggleClass('signupSwitchActive');
		}

		// Hide the email signup and show social signup
		$('.signupEmail').hide();
		$('.signupSocial').show();

	});

});
