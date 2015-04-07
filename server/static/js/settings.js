$(document).ready(function() {
	// Jquery Password Strength Plugin; sitepoint.com/developing-password-strength-plugin-jquery/

	$('#btn-validate-code').click(function(e) {
		console.log ('validate code');
		//verify_email_js();
	});

	$('#btn-get-verified').click(function(e) {
		e.preventDefault();
		console.log ('validate code');
		email = $("#email").val();
		console.log ('validate code' + email);
		$("#verify-notice").html("Verification code sent to "+ email);
		$("#verify-email").slideDown();
		console.log ('send _ VERIFICATION _ EMAIL ');
//		send_verification_email();
		$("#btn-get-verified").hide();
	});


	$('#btn-back').click(function(e){
		window.location.href = "/dashboard";
	});

	$('#btn-save').click(function(e){
		e.preventDefault();
		save_settings();
	});

});


function save_settings() {
	console.log('save_settings');
	var fd = new FormData($('#settings-form')[0]);
	$("#settings-status").html("Saving...").fadeIn();

	// Remove error indicators
	//$("#passMeter").slideUp().html("");
	$('.field.error').slideUp().html("");
	$('.field.input').css("border-color", "#e1e8ed");

	$.ajax({ url	: "/settings/update",
			type	: "POST",
			data : fd,
			processData: false,
  			contentType: false,
			success : function(response) {
			 	console.log("AJAX - successfully saved");		 	

				$("#update_password, #verify_password, #current_password").val('');
				$("#settings-status").html("<span class='success'>"+response.usrmsg+"</span>").fadeIn(400);
			 	//$("#passMeter").slideUp().html("");

				setTimeout(function() {
					$('#settings-status').fadeOut(400);
				}, 1600);
			},
			error: function(xhr, status, error) {
				console.log(["AJAX - error.", error]);
				var err = JSON.parse(xhr.responseText);
				var errors = err.errors;
				
				console.log("FORM ERRORS:");
				console.log(JSON.stringify(errors));
				showErrors(errors);
			}
	});
	return false;
}


/*
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

function showErrors(errors) {
	$('#settings-status').empty();

	$.each(errors, function(e, error){
		// "e" here would be the form element name that has the error, e.g. "prof_name"
		var element = "#"+e;
		console.log("show-error: ["+element + " : " + error + "]");

		if (element == '#verify_password') {
			$("#update_password").prev(".field.error").html(error).slideDown();
			$('#update_password').css("border-color", "#e75f63");
			$('#verify_password').css("border-color", "#e75f63");
		} else {
			$(element).prev(".field.error").html(error).slideDown();
			$(element).css("border-color", "#e75f63");
		}
	});

	$('#settings-status').html("<span class='error'>There was a problem.</span>").fadeIn();
}
