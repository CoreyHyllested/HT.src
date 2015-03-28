$(document).ready(function () {
	console.log('modals.js: ready');
	$('#modal-close').click(function (e)	{ closeAlertWindow(); } );
	$('#modal-dismiss').click(function (e)	{ closeAlertWindow(); } );
	$('.dismiss-modal').click(function (e)	{ closeAlertWindow(); } );

	$(document).keyup(function(e) {
		/* close overlay if ESC is hit */
		if (e.keyCode == 27) /* ESC */ {
			if ($('#modal-wrap').hasClass('window-visible') && $('#modal-window').hasClass('window-alert')) {
					closeAlertWindow();
			}
		}
	});

	/* MAYBE:
		$('#overlay').click( function (e) { closeAlertWindow(); } );
		$('.alertButton').click( function (e) { closeAlertWindow(); } );
	*/
});

function openAlertWindow(text) {
	$('#overlay').addClass('overlay-dark').addClass('dismiss-modal');
	$('#modal-message').html(text);
	$('#modal-wrap').addClass('window-visible')
	$('#modal-window').addClass('window-alert');

	return false;
}


function notifyUser(txt) {
	return openAlertWindow(text);
}

function closeNotification() { }

function closeAlertWindow() {
	$('#overlay').removeClass('overlay-dark');
	/* .removeClass('dismiss-modal'); CAH: adds right, but prevents dismissal */
	$('#modal-wrap').removeClass('window-visible');
	$('#modal-window').removeClass('window-alert');
	$('#modal-message').html('');
	return false;
}
