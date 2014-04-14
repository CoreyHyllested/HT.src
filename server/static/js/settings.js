$(document).ready(function() {

	// On mobile, switch to email settings
	$('.settingsSwitchEmail').click(function() {

		// If not highlighted, make it so
		if (!$(this).hasClass('settingsSwitchActive')) {
			$(this).toggleClass('settingsSwitchActive');
		}

		// Take away the highlight from either of the other two tabs
		if ($('.settingsSwitchPassword').hasClass('settingsSwitchActive')) {
			$('.settingsSwitchPassword').toggleClass('settingsSwitchActive');
		}

		else if ($('.settingsSwitchPayout').hasClass('settingsSwitchActive')) {
			$('.settingsSwitchPayout').toggleClass('settingsSwitchActive');
		}

		// Hide the other two tabs and show email settings
		$('.settingsPassword').hide();
		$('.settingsPayout').hide();
		$('.settingsEmail').show();	
	});



	// On mobile, switch to password settings
	$('.settingsSwitchPassword').click(function() {

		// If not highlighted, make it so
		if (!$(this).hasClass('settingsSwitchActive')) {
			$(this).toggleClass('settingsSwitchActive');
		}

		// Take away the highlight from either of the other two tabs
		if ($('.settingsSwitchEmail').hasClass('settingsSwitchActive')) {
			$('.settingsSwitchEmail').toggleClass('settingsSwitchActive');
		}

		else if ($('.settingsSwitchPayout').hasClass('settingsSwitchActive')) {
			$('.settingsSwitchPayout').toggleClass('settingsSwitchActive');
		}

		// Hide the other two tabs and show email settings
		$('.settingsEmail').hide();
		$('.settingsPayout').hide();
		$('.settingsPassword').show();
	});



	// On mobile, switch to payout settings
	$('.settingsSwitchPayout').click(function() {

		// If not highlighted, make it so
		if (!$(this).hasClass('settingsSwitchActive')) {
			$(this).toggleClass('settingsSwitchActive');
		}

		// Take away the highlight from either of the other two tabs
		if ($('.settingsSwitchEmail').hasClass('settingsSwitchActive')) {
			$('.settingsSwitchEmail').toggleClass('settingsSwitchActive');
		}

		else if ($('.settingsSwitchPassword').hasClass('settingsSwitchActive')) {
			$('.settingsSwitchPassword').toggleClass('settingsSwitchActive');
		}

		// Hide the other two tabs and show email settings
		$('.settingsEmail').hide();
		$('.settingsPassword').hide();
		$('.settingsPayout').show();
	});
});