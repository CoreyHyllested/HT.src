var feedback_version = 0.13;

function __get_json(string) {
	try {
		return JSON.parse(string);
	} catch (e) {
		console.log('String isnt (parsable) JSON');
		console.log(string);
		return null;
	}
}


function show_errors(status_element, responseText) {
	console.log("show_errors()");
	set_status(status_element, 'There was an issue');

	response = __get_json(responseText);
	if (!response || !response.errors) return;

	$.each(response.errors, function(e, error) {
		// e is the element with the error, e.g. "prof_name"
		var element = "#"+e;
		console.log("show-error: ["+element + " : " + error + "]");
//		$(element).prev(".ff.error").html(error).slideDown();
		$(element).css("border-color", "#e75f63");
	});
}
function clear_error_msg(element) { $(element).prev(".ff.error").slideUp().html('');	}
function clear_error_box(element) { $(element).css("border-color", "#e1e8ed");			}


function set_status(query, content) {
	$(query).empty();
	$(query).html(content).fadeIn();
	setTimeout(feedback_fade,	2500, query);
}

function positive_feedback(content)	{
	html = $('<li class="feedback-bubble">' + content + '</li>').uniqueId().appendTo('#feedback');
	feedback_timeout(html);
}

function negative_feedback(content)	{
	html = $('<li class="feedback-bubble feedback-negative">' + content + '</li>').uniqueId().appendTo('#feedback');
	feedback_timeout(html);
}

function feedback_fade(query)	{	$(query).fadeOut("slow");	}
function feedback_remove(query)	{	$(query).remove();			}
function feedback_timeout(msg)	{
	uid	= msg.attr('id');
	setTimeout(feedback_fade,	2500, '#' + uid);
	setTimeout(feedback_remove, 5000, '#' + uid);
}


$(document).ready(function () {
	console.log('feedback.js: v' + feedback_version);
});

