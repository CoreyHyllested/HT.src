version = 1.08;

$(document).ready(function () {
	console.log('modals.js: v'+version);
	$('#modal-close').on('click', shut_modal_window);
	$('#modal-wrap').on('click', '.dismiss-modal', shut_modal_window);

	$(document).keyup(function(e) {
		/* close overlay when ESC is hit */
		if (e.keyCode == 27) { shut_modal_window(); }
	});
});

function open_modal_window() {
	$('#overlay').addClass('overlay-dark');
	$('#modal-wrap').addClass('active')
	$('#modal-window').show();
}

function shut_modal_window() {
	$('#modal-window').hide().removeClass('window-border');
	$('#modal-wrap').removeClass('active');
	$('#overlay').removeClass('overlay-dark').removeClass('overlay-light');
	$('#modal-message').html('');
	$('#modal-buttons').hide();
	return false;
}

function openAlertWindow(text) {
	$('#modal-message').html(text);
	$('#modal-buttons').show();
	open_modal_window();
	return false;
}

function closeAlertWindow() {
	return shut_modal_window();
}

function open_task_window(embed) {
	$('#modal-message').html(embed);
	open_modal_window();
}


function openModalLogin()	{ return __get_login('#account-email');		}
function openModalSocial()	{ return __get_login('#account-social');	}


function __get_login(set_active) {
	$.ajax({type	: 'GET',
			url		: '/modal/login',
			success : function(response) {
				open_task_window(response.embed);
				$(set_active).addClass('login-active');
			},
			error: function(xhr, status, error) {
				console.log(['ajax failure', xhr]);
				//rc = JSON.parse(xhr.responseText);
			}
	});
	return false;
}


function add_new_business() {
	fd = {};
	fd.name = $('#trusted').val();
	fd.csrf_token = $('#csrf_token').val();

	console.log('add new business ' + fd.name);
	$.ajax({type	: 'GET',
			url		: '/business/new',
			data	: fd,
			contentType: false,
			success : function(response) {
				console.log(response);
				open_task_window(response.embed);
				$('#phone').mask("(999) 999-9999");
			},
			error: function(xhr, status, error) {
				console.log(['ajax error', xhr]);
				if (status == 401) { window.location.href = '/login'; }
				//rc = JSON.parse(xhr.responseText);
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
					$('#modal-wrap').addClass('active');
					$('#modal-window').show().addClass('window-border');
					$('#modal-buttons').html("<input type='button' class='btn-modal whiteButton dismiss-modal' value='Cancel'></input><input type='button' class='btn-modal blueButton' value='Share'></input>");
				}
			},
			error: function(xhr, status, error) {
				console.log(['ajax failure', xhr]);
				rc = JSON.parse(xhr.responseText);
			}
	});
}


