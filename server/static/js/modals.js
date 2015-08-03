version = 1.05;

$(document).ready(function () {
	console.log('modals.js: v'+version);
	$('#modal-close').click(function (e)	{ closeAlertWindow(); } );
	$('#modal-wrap').on('click', '.dismiss-modal', closeAlertWindow);
	$('#modal-dismiss').click(function (e)	{ closeAlertWindow(); } );

	$(document).keyup(function(e) {
		/* close overlay if ESC is hit */
		if (e.keyCode == 27) /* ESC */ {
			if ($('#modal-wrap').hasClass('modal-active') && $('#modal-window').hasClass('window-alert')) {
				closeAlertWindow();
			}
		}
	});
});

function openAlertWindow(text) {
	$('#overlay').addClass('overlay-dark');
	$('#modal-message').html(text);
	$('#modal-wrap').addClass('modal-active')
	$('#modal-window').addClass('window-alert');
	return false;
}


function notifyUser(txt) {
	return openAlertWindow(text);
}

function closeNotification() { }

function openModalLogin()	{ return __get_login('#account-email');		}
function openModalSocial()	{ return __get_login('#account-social');	}


function __get_login(set_active) {
	$.ajax({ url	: '/modal/login',
			type	: 'GET',
			success : function(response) {
				if (response.embed) {
					$('#overlay').addClass('overlay-light');
					$('#modal-message').html(response.embed);
					$('#modal-wrap').addClass('modal-active');
					$('#modal-window').addClass('window-alert').addClass('window-border');
					$('#modal-buttons').html("<input type='button' class='btn btn-modal whiteButton dismiss-modal' value='Cancel'></input><input type='button' class='btn btn-modal blueButton' value='Sign in'></input>");
					$(set_active).addClass('login-active');
				}
			},
			error: function(xhr, status, error) {
				console.log(['ajax failure', xhr]);
				rc = JSON.parse(xhr.responseText);
			}
	});
	return false;
}


function modal_to_email() {
	$('#account-social').removeClass('login-active');
	$('#account-email').addClass('login-active');
}

function openModalShare() {
	fd = new FormData();
	fd.append("csrf_token", $('#csrf_token').val());

	$.ajax({ url	: '/share/email',
			type	: 'POST',
			data	: fd,
			processData: false,
			contentType: false,
			success : function(response) {
				//console.log(response);
				if (response.embed) {
					$('#overlay').addClass('overlay-light')
					$('#modal-message').html(response.embed);
					$('#modal-wrap').addClass('modal-active');
					$('#modal-window').addClass('window-alert').addClass('window-border');
					$('#modal-buttons').html("<input type='button' class='btn-modal whiteButton dismiss-modal' value='Cancel'></input><input type='button' class='btn-modal blueButton' value='Share'></input>");
				}
			},
			error: function(xhr, status, error) {
				console.log(['ajax failure', xhr]);
				rc = JSON.parse(xhr.responseText);
			}
	});
}

function closeAlertWindow() {
	$('#overlay').removeClass('overlay-dark').removeClass('overlay-light');
	/* .removeClass('dismiss-modal'); CAH: adds right, but prevents dismissal */
	$('#modal-wrap').removeClass('modal-active');
	$('#modal-window').removeClass('window-alert').removeClass('window-border');
	$('#modal-message').html('');
	return false;
}
