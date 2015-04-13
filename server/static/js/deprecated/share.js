function share_sc() {
	var fd = {};
	var missing = 0;

	console.log('share_sc() enter');
	fd.recipient = $('#recipient').val();
	fd.subject = $('#subject').val();
	fd.composeBody = $('#composeBody').val();
	//fd.csrf_token = $('#csrf').val();		//currently unused.

	$.each(fd, function(k, v) { console.log(k+ ": " + v); });

	// ensure all fields exist.
	$.each(fd, function(k, v) { 
		$('#'+k).removeClass('formFieldError');
		if ((v == null) || (v == '')) { 
			console.log("missing: " + k);
			$('#'+k).addClass('formFieldError');
			missing++; 
		}
		console.log(k+ ": " + v);
	 });
	if (missing) { return false; }


	$.ajax({url  : '/email/share/friend',
			type : 'POST',
			data : fd,
			dataType: 'json',
			success : function(data) {
						console.log('sent verification emails');
						$("#shareStatus").html("<span class='success'>Email sent.</span>");
						setTimeout(function() {
							closeModal();
						}, 5000);
			},
			error : function(response) {
						console.log("Error - " + response.usrmsg);
						$("#shareStatus").html("<span class='success'>Something went wrong..</span>");
						$.each(response, function(k, v) { console.log(k+ ": " + v); });
			}
	});
	console.log('share_sc() exit');
	return false;
} 



$(document).ready(function() {
	console.log('initalizing');
	$('#sendMessage').click(share_sc);
});
