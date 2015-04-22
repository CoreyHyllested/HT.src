VERSION = 1.4
$(document).ready(function () {
	console.log('dashboard.js: v' + VERSION);

	$('#send-requests').click(function (e)	{ 
		e.preventDefault();
		email = $('#invite_emails').val()
		console.log('clicked...' + email);
		sendrequest();
	} );
});
	

function sendrequest() {
	console.log('send-request()');
	var fd = new FormData($('#review-request')[0]);
	$.each(fd, function(k, v) {
		console.log('project fd['+k+']='+v);
	});

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
					//$('.request[data-id='+response.brid+']').css('background-color', '#ff00ff');
				} else {
					console.log(response.embed);
					$('#requests').append(response.embed);
				}

			},
			error: function(xhr, status, error) {
				console.log(['ajax failure', xhr]);
				rc = JSON.parse(xhr.responseText);
				console.log(rc['sc_msg']);
				//openAlertWindow(rc['sc_msg']);
			}
	});
	return false;
}
