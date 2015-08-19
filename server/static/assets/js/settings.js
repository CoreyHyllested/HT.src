var settings_version = 0.04;

console.log('settings.js: v' + settings_version);

function settings_submit(event) {
	event.preventDefault();

	var fd = new FormData(this);
	set_status('.action-feedback', 'Saving...');

	// Remove error indicators
	//$("#passMeter").slideUp().html("");
	$('.field-error').html('').removeClass('error');
	$('input.error').removeClass('error');

	$.ajax({ url	: "/settings/update",
			type	: "POST",
			data : fd,
			processData: false,
  			contentType: false,
			success : function(xhr) {
				$("#update_password, #verify_password, #current_password").val('');
				set_status('.action-feedback', xhr.status);	// change /settings/update to use whatever was used in /auth/signin
			 	//$("#passMeter").slideUp().html("");
			},
			error: function(xhr, status, error) {
				console.log("Ajax error", status);
				show_errors('.action-feedback', xhr.responseJSON);
			}
	});
	return false;
}



/*
	// Jquery Password Strength Plugin; sitepoint.com/developing-password-strength-plugin-jquery/

	$('#verify_password').keyup(function(){ initializeStrengthMeter(); });
	$('#update_password').keyup(function(){ if ($('#verify_password').val() != "") { initializeStrengthMeter(); } });
function initializeStrengthMeter() {
	$("#passMeter").PasswordStrengthManager({
		password: $("#update_password").val(),
		confirm_pass : $('#verify_password').val(),
		blackList : ["efewf"], 
		minChars : '6',
		maxChars : '50',
		advancedStrength : false
	});
}
*/

$(document).ready(function() {
	$('#btn-get-verified').click(function(e) { /* see git for code (8/18/15) */ });
	$('#btn-back').click(function(e){ window.location.href = "/profile"; });
	$('#form-settings').on('submit', settings_submit);
});

