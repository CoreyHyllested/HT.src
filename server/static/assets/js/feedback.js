var feedback_version = 0.19;

function __get_json(string) {
//	response = __get_json(responseText);
//	if (!response || !response.errors) return;
	try {
		return JSON.parse(string);
	} catch (e) {
		console.log('String isnt (parsable) JSON');
		console.log(string);
		return null;
	}
}


function show_errors(status_element, responseJSON) {
	set_status(status_element, responseJSON.status || 'There was an issue');

	$.each(responseJSON.errors, function(e, error) {
		// e is the element with the error, e.g. "prof_name"
		var element = "#"+e;
		console.log("show-error: ["+element + " : " + error + "]");
		$(element).prev('.field-error').addClass('error').html(error).slideDown();
		$(element).addClass('error');
	});
}


function clear_error_msg(element)	{ $(this).prev('.field-error').slideUp().html('').removeClass('error');	}
function clear_error_box(element)	{ $(this).removeClass('error');	}

function flash_elem_border(elem)	{ highlight_element(elem);		setTimeout(highlight_disable, 1000, elem);	}
function highlight_element(elem)	{ $(elem).addClass('highlight');	}
function highlight_disable(elem)	{ $(elem).removeClass('highlight');	}




function set_status(elem, content, time) {
	time = (typeof time !== 'undefined') ? time : 2500;
	$(elem).empty();
	$(elem).html(content).fadeIn();
	setTimeout(feedback_fadeout, time, elem);
}

function positive_feedback(content)	{
	element = $('<li class="feedback-bubble">' + content + '</li>').uniqueId().appendTo('#feedback');
	feedback_timeout(element);
}

function negative_feedback(content)	{
	element = $('<li class="feedback-bubble feedback-negative">' + content + '</li>').uniqueId().appendTo('#feedback');
	feedback_timeout(element);
}

function feedback_fadeout(e_id)	{	$(e_id).fadeOut('slow');	}
function feedback_slideup(e_id)	{	$(e_id).slideUp('slow');	}
function feedback_timeout(elem)	{
	uid	= elem.attr('id');
	setTimeout(feedback_fadeout, 2500, '#' + uid);
	setTimeout(feedback_slideup, 5000, '#' + uid);
}


$(document).ready(function () {
	console.log('feedback.js: v' + feedback_version);
	$('body').on('focus', 'input.error', clear_error_box);
	$('body').on('blur',  'input',		 clear_error_msg);
});

