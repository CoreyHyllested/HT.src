var feedback_version = 0.14;

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
//		$(element).prev(".ff.error").html(error).slideDown();
//		$(element).prev('.field.error').html(error).slideDown();	//settings only, I belive
		$(element).css("border-color", "#e75f63");
	});
}


function clear_error_msg(element)	{ $(element).prev(".ff.error").slideUp().html('');	}
function clear_error_box(element)	{ $(element).css("border-color", "#e1e8ed");		}


function set_status(elem, content) {
	$(elem).empty();
	$(elem).html(content).fadeIn();
	setTimeout(feedback_fadeout, 2500, elem);
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
	$('body').on('blur', '.field.input',		clear_error_box);
	$('body').on('blur', 'input.form-control',	clear_error_box);
});

