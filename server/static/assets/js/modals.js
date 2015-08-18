version = 1.11;


function open_modal_window(embed, win_sz) {
	$('#modal-message').html(embed);

	$('#overlay').addClass('overlay-dark');
	$('#modal-wrap').addClass('active');
	$('#modal-window').addClass(win_sz);
	$('#modal-window').show();
}

function shut_modal_window() {
	$('#modal-window').hide().removeClass('black-border');	//remove all win_sz classes
	$('#modal-wrap').removeClass('active');
	$('#overlay').removeClass('overlay-dark').removeClass('overlay-light');
	$('#modal-message').html('');
	$('#modal-buttons').hide();
	return false;
}

function openAlertWindow(text) {
	$('#modal-buttons').show();
	open_modal_window(text);
	return false;
}

function closeAlertWindow() {
	return shut_modal_window();
}

function open_task_window(embed, win_sz) {
	open_modal_window(embed, win_sz);
}


function open_email(status)	{ return __get_signin(status, '#account-signin');	}
function open_login(status)	{ return __get_signin(status, '#account-social');	}


function __get_signin(status, set_active) {
	$.ajax({type	: 'GET',
			url		: '/modal/login',
			success : function(response) {
				open_task_window(response.embed, 'sz-320');
				$('#'+status).toggleClass('no-display');
				$(set_active).toggleClass('no-display');
			},
			error	: function(xhr, status, error) {
				console.log('ajax failure', xhr);
			}
	});
	return false;
}


function __login_with_email() {
	$('#account-social').addClass('no-display');
	$('#account-signin').removeClass('no-display');
}

function __login_with_social() {
	$('#account-social').removeClass('no-display');
	$('#account-signin').addClass('no-display');
}



function signin_submit(event) {
	event.preventDefault();	//prevent submit.
	fd	= new FormData(this)

	set_status('.action-feedback', 'Attempting sign in');

	$.ajax({type		: 'POST',
			url			: '/authorize/signin',
			data		: fd,
			processData	: false,
			contentType	: false,
			success 	: function(xhr) {
							set_status('.action-feedback', 'Attempting thinks its successful');
							window.location.href = xhr.next;
						},
			error		: function(xhr, status, error) {
							console.log("AJAX Error", xhr);
							if (xhr.status === 400) {
								show_errors('.action-feedback', xhr.responseJSON);
							} else { }
							// 401 not possible here
						}
	});
	return false;
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
					$('#modal-wrap').addClass('active');
					$('#modal-window').show().addClass('black-border');
					$('#modal-buttons').html("<input type='button' class='btn-modal whiteButton dismiss-modal' value='Cancel'></input><input type='button' class='btn-modal blueButton' value='Share'></input>");
				}
			},
			error: function(xhr, status, error) {
				console.log(['ajax failure', xhr]);
				rc = JSON.parse(xhr.responseText);
			}
	});
}



$(document).ready(function () {
	console.log('modals.js: v'+version);
	$('#modal-close').on('click',					shut_modal_window);
	$('#modal-wrap').on('click',  '.dismiss-modal',	shut_modal_window);
	$('#modal-message').on('submit', '#account-signin', signin_submit);

	$(document).keyup(function(e) {
		/* close overlay when ESC is hit */
		if (e.keyCode == 27) { shut_modal_window(); }
	});
});

