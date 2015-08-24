VERSION = 1.6
$(document).ready(function () {
	console.log('dashboard.js: v' + VERSION);

	$('#send-requests').click(function (e)	{ 
		e.preventDefault();
		fd = new FormData($('#review-request')[0]);
		sendrequest(fd);
	} );

	$('#requests').on('click', '.request .resend', function(e) {
//		data = $(this).parent().data('id');
//		console.log('clicked...' + data);
		mail = $(this).parent().data('email');
		csrf = $('#csrf_token').val();
		fd = new FormData();
		fd.append("invite_emails", mail);
		fd.append("resend_emails", true);
		fd.append("csrf_token", csrf);
		sendrequest(fd);
	});
});
	

function sendrequest(fd) {
	console.log('send-request()');

	$.ajax({ url	: '/review/request',
			type	: 'POST',
			data	: fd,
			processData: false,
  			contentType: false,
			success : function(response) {
				console.log('ajax Success');
				console.log(response);
				if (response.brid) {
					console.log('brid exists' + response.brid);
				//	$('.request[data-id='+response.brid+']').css('background-color', '#ff00ff');
				} else {
					console.log(response.embed);
					$('#requests').append(response.embed);
				}

			},
			error: function(xhr, status, error) {
				console.log(['ajax failure', xhr]);
				rc = JSON.parse(xhr.responseText);
				openAlertWindow(rc['sc_msg']);
			}
	});
	return false;
}
