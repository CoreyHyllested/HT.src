var settings_version = 0.2;

console.log('settings.js: v' + settings_version);

$(document).ready(function() {
	$('#btn-get-verified').click(function(e) {
		e.preventDefault();
		email = $("#email").val();
		console.log ('validate code' + email);
		$("#verify-notice").html("Verification sent.");
		$("#verify-email").removeClass('empty');
		$("#verify-email").slideDown();
		send_verification_email();
		$("#btn-get-verified").hide();
	});

	$('#btn-validate-code').click(function(e) {
		e.preventDefault();
		console.log('validate code');
		validate_challenge_hash();
	});


	$('#btn-back').click(function(e){
		window.location.href = "/dashboard";
	});

	$('#btn-save').click(function(e){
		e.preventDefault();
		save_settings();
	});
});



function send_verification_email() {
	console.log('send_verification_email()');
	var fd = {};
	fd.email_addr = $('#email').val();
	fd.csrf_token = $('#csrf').val();

	$.each(fd, function(k, v) { console.log(k+ ": " + v); });
	$.ajax({ url : '/email/request-verification/me',
			 type : 'POST',
			 data : fd,
			 success : function(data) {
				 console.log('sent verification emails');
			}
	});
}

function validate_challenge_hash() {
	console.log("verify_email_js: begin");
	var challenge = $('#challenge').val();

	var fd = {};
	fd.email = $('#email').val();
	fd.csrf_token = $('#csrf').val();
	fd.next_url   = $('#nexturl').val();
	$.each(fd, function(k, v) { console.log(k+ ": " + v); });


	$.ajax({ url : '/email/verify/'+challenge,
			 type : 'POST',
			 data : fd,
			 dataType: 'json',
			 success : function(data) {
				console.log ('/email/verify - success');
				$(".emailVerifyText").html("<span class='success'>Email successfully verified!</span>");
				$(".emailVerifyStatus").html("<div class='verifySuccess'><i class='fa fa-fw fa-check'></i>Email verified.</div>");
				setTimeout(function() {
					$('.emailVerifyInput').slideUp(1000);
				}, 2000);
				return false;
			 },
			 error: function(data) {
				console.log ('/email/verify - error');
			 	$(".emailVerifyText").html("<span class='error'>Sorry, that code didn't work.</span>");
			 }
	});
	return false;
}


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
