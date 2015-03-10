$(document).ready(function() {
	$('.formField').focus(function(e) {
		console.log(this);
		$(this).nextAll(".formFieldError:first").html('');
	});

	$('.formField').blur(function(e) {
		$(this).css("border-color", "#e1e8ed");
	});

	$(".save-project").click(function(e) {
		e.preventDefault();
		saveProject();
	});

	$('#schedule_phone').click(function(e) {
		kick(e);
	});

	$('#schedule_email').click(function(e) {
		console.log('schedule email');
		kick(e);
	});

	enableNS();
});

function kick(e) {
	e.preventDefault();
	console.log('kick');
	setTimeout(function() { location.pathname='/dashboard'; }, 1500);
}


function saveProject() {
	console.log("save project");
	var fd = new FormData($('#project-details')[0]);
	$.each(fd, function(k, v) {
		console.log('project fd['+k+']='+v);
	});

	// reset ALL error indicators
	$(".formFieldError").html("");
	$(".formField").css("border-color", "#e1e8ed");

	$.ajax({ url	: "/project/update",
			type	: "POST",
			data	: fd,
			processData: false,
  			contentType: false,
			success : function(response) {
				$('#proj_id').val(response.proj_id);

				console.log('Fade success in and out, set proj_id: ' + response.proj_id);
				$('.save-btn-text').fadeTo('slow', 0);
				setTimeout(function() {
					$('.save-btn-text').text('Successfully Saved!'); /* .css('color', 'green'); */
					$('.save-btn-text').fadeTo('slow', 1);
				}, 1000);

				setTimeout(function() { $('.save-btn-text').fadeTo('slow', 0); }, 2500);
				setTimeout(function() {
					$('.save-btn-text').text('Save project'); /* .css('color', '#29abe2'); */
					$('.save-btn-text').fadeTo('slow', 1);
				}, 4000);
				enableNS();
			},

			error: function(xhr, status, error) {
				var err = JSON.parse(xhr.responseText);
				var errors = err.errors;
				console.log(JSON.stringify(errors));
				showErrors(errors);
			}
	});
	return false;
}

function enableNS() {
	id = $('#proj_id').val();

	if (id != 'new') {
		$.each($('.disabled'), function () {
			console.log('nextstep class elem ' + $(this));
			$(this).removeClass('disabled');
		});
	}
}



function showErrors(errors) {
	// highlight each error/element for users
	$.each(errors, function(element, error) {
		var e = "#"+element;
		console.log("error: " + element + " => " + error);
		$(e).nextAll(".formFieldError:first").html(error).fadeIn();
		$(e).css("border-color", "red");
	});
	// create error count and set it on submit button; count down. 'Fix X errors and Submit'
}

