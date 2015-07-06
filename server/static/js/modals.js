$(document).ready(function () {
	console.log('modals.js: ready');
	$('#modal-close').click(function (e)	{ closeAlertWindow(); } );
	$('#modal-dismiss').click(function (e)	{ closeAlertWindow(); } );
	$('.dismiss-modal').click(function (e)	{ closeAlertWindow(); } );

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
	$('#overlay').addClass('overlay-dark').addClass('dismiss-modal');
	$('#modal-message').html(text);
	$('#modal-wrap').addClass('modal-active')
	$('#modal-window').addClass('window-alert');
	return false;
}


function notifyUser(txt) {
	return openAlertWindow(text);
}

function closeNotification() { }

function openModalLogin() {
	fd = new FormData();
	fd.append("csrf_token", $('#csrf_token').val());

	$.ajax({ url	: '/login/modal/email',
			type	: 'POST',
			data	: fd,
			processData: false,
			contentType: false,
			success : function(response) {
				console.log(response);
				if (response.embed) {
					console.log(response.embed);
					$('#overlay').addClass('overlay-light').addClass('dismiss-modal');
					$('#modal-message').html(response.embed);
					$('#modal-wrap').addClass('modal-active');
					$('#modal-window').addClass('window-alert').addClass('window-border');
					$('#modal-dismiss').html("<input type='button' class='btn btn-modal whiteButton' value='Cancel'></input><input type='button' class='btn btn-modal blueButton' value='Sign in'></input>");
					$('#account-email').addClass('active');
				}
			},
			error: function(xhr, status, error) {
				console.log(['ajax failure', xhr]);
				rc = JSON.parse(xhr.responseText);
			}
	});
	return false;
}

function openModalSocial() {
	fd = new FormData();
	fd.append("csrf_token", $('#csrf_token').val());

	$.ajax({ url	: '/login/modal/email',
			type	: 'POST',
			data	: fd,
			processData: false,
			contentType: false,
			success : function(response) {
				console.log(response);
				if (response.embed) {
					console.log(response.embed);
					$('#overlay').addClass('overlay-light').addClass('dismiss-modal');
					$('#modal-message').html(response.embed);
					$('#modal-wrap').addClass('modal-active');
					$('#modal-window').addClass('window-alert').addClass('window-border');
					$('#modal-dismiss').html("<input type='button' class='btn btn-modal whiteButton' value='Cancel'></input><input type='button' class='btn btn-modal blueButton' value='Sign in'></input>");
					$('#account-social').addClass('active');
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
	$('#account-social').removeClass('active');
	$('#account-email').addClass('active');
}

function openModalShare() {
	console.log('here');
	fd = new FormData();
	fd.append("csrf_token", $('#csrf_token').val());

	$.ajax({ url	: '/share/email',
			type	: 'POST',
			data	: fd,
			processData: false,
			contentType: false,
			success : function(response) {
				console.log(response);
				if (response.embed) {
					console.log(response.embed);
					$('#overlay').addClass('overlay-light').addClass('dismiss-modal');
					$('#modal-message').html(response.embed);
					$('#modal-wrap').addClass('modal-active');
					$('#modal-window').addClass('window-alert').addClass('window-border');
					$('#modal-dismiss').html("<input type='button' class='btn btn-block whiteButton' value='Cancel'></input><input type='button' class='btn btn-block blueButton' value='Share'></input>");
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
