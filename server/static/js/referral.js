var referral_version = 0.61;

function clear_profile() {
	$('#profile-card').addClass('no-display');
	$('#refer-explanation').addClass('no-display');
}

function save_business_clicked() {
	fd = new FormData();
	fd.append("csrf_token", $('#csrf_token').val());
	fd.append("name", $('#name').val());
	fd.append("site", $('#site').val());
	fd.append("email", $('#email').val());
	fd.append("phone", $('#phone').val());

	submit_new_business(fd);
}

function feedback_fade(id)		{	$('#'+id).fadeOut("slow");	}
function feedback_remove(id)	{	$('#'+id).remove();			}
function add_feedback(content)	{
	html = $('<li class="feedback-bubble">' + content + '</li>').uniqueId().appendTo('#feedback');
	uid	 = $(html).attr('id');
	setTimeout(feedback_fade,	2500, uid);
	setTimeout(feedback_remove, 5000, uid);
}



function modal_create_business() {
	fd = {};
	name = $('#refer-professional .form-control.tt-input').val();
	fd.name = name;
	fd.csrf_token = $('#csrf_token').val();
	modalCreateBusiness(fd);

	return false;
}


function modalCreateBusiness(fd) {
	console.log('create business ' + fd.name);
	console.log(fd);
	$.ajax({ url	: '/business/create?name=' + fd.name,
			type	: 'GET',
			processData: false,
			contentType: false,
			success : function(response) {
				console.log(response);
				if (response.embed) {
					$('#modal-message').html(response.embed);

					$('#overlay').addClass('overlay-dark');
					$('#modal-wrap').addClass('modal-active');
					$('#modal-window').addClass('window-alert');
					$('#modal-buttons').html("<input type='button' class='btn btn-modal whiteButton dismiss-modal' value='Cancel'></input><input type='button' class='btn btn-modal blueButton save-business' value='Create'></input>");
				}
			},
			error: function(xhr, status, error) {
				console.log(['ajax failure', xhr]);
				rc = JSON.parse(xhr.responseText);
			}
	});
	return false;
}


function submit_new_business(fd) {
	console.log('submitting new business ' + fd.name);
	$.ajax({ url	: '/business/create',
			type	: "POST",
			data	: fd,
			processData: false,
			contentType: false,
			success : function(response) {
				console.log(response);
				closeAlertWindow();

				var profile_fd = {};
				profile_fd.csrf_token = "{{ csrf_token() }}";
				profile_fd.profile_id = response.business.business_id;
				get_profile(profile_fd);
				add_feedback('Added ' + response.business.business_name);
			},
			error	: function(data) {
				console.log("Oops, AJAX Error.");
				console.log(data);
			}
	});
}

function save_referral(evt) {
	fd = {};
	fd.csrf_token	= "{{ csrf_token() }}";
	fd.business	= $('#profile-card').data('id');
	fd.referral	= $('#referral-profile').attr('data-id');
	fd.content	= $('#refer-why').val();
	fd.projects	= $('#refer-proj').val();

	console.log('save_referral');
	console.log(fd.business);
	console.log(fd.referral);
	console.log(fd.content);
	console.log(fd.projects);

	referral_uri = "/referral/create";
	if (fd.referral != "") {
		referral_uri = "/referral/" + fd.referral + "/update";
	}

	$.ajax({	url		: referral_uri,
				type	: "POST",
				data	: fd,
				success : function(data) {
					console.log(data);
					$('#referral-profile').attr('data-id', data.ref_uuid);
					add_feedback('Saved');
				},
				error	: function(data) {
					console.log("Oops, AJAX Error.");
					console.log(data);
				}
	});

}

pro_finder = new Bloodhound({
	datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
	queryTokenizer: Bloodhound.tokenizers.whitespace,
	remote: {
		url: '/business/search/%QUERY',
		wildcard: '%QUERY'
	}
});

projects = new Bloodhound({
	datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
	queryTokenizer: Bloodhound.tokenizers.whitespace,
	prefetch: {
	url: "/projects.json",
		filter: function(list) {
			return $.map(list, function(project_name) { return { 'name' : project_name }; });
		}
	}
});


function get_profile(fd) {
	$.ajax({	url		: "/business/id/" + fd.profile_id,
				type	: "POST",
				data	: fd,
				success : function(data) {
					$('#refer-explanation').removeClass('no-display');
					$('#profile-card').removeClass('no-display');
					$('#profile-card').attr('data-id', fd.profile_id);

					busname = data.business_name
					if (data.business_website) {
						busname = '<a href="' + data.business_website + '" target="_blank">' + busname + '</a>'
					}
					$('#pro-name').html(busname);
					/* examples of setting phone, email in git-log (july-21-15) */
					$('#refer-why').focus();
				},
				error	: function(data) {
					console.log("Oops, AJAX Error.");
				}
	});
}


function clear_business_addr( event ) {
	name = $('#invite_emails').val();
	idx = name.lastIndexOf(" | ")
	if (idx == -1) { return; }
	strng = name.substring(0, name.lastIndexOf(" | "));
	$('#invite_emails').val(strng);
}


$(document).ready(function () {
	console.log('referral.js: v' + referral_version);

	$('#refer-professional .typeahead').typeahead({
		hint: true,
		highlight: true,
		minLength: 4,
	},
	{
		display: 'combined',
		source: pro_finder,
		templates: {
			notFound: function(q) {
				return '<div id=\'not-found\'>We did not match \"' + q.query + '\".<br><a href="javascript:modal_create_business();">Add this business?</a></div>';
			},
			pending: '<div>Searching...</div>',
			suggestion: Handlebars.compile('<div class="pro-suggestion" data-id={{id}}>{{name}} <span class="pro-suggestion-addr">{{addr}}</span></div>')
		}
	});





	projects.initialize();

	$('#invite_emails').keydown(function(event) {
		clear_profile();
	});
	$('#modal-buttons').on('click', '.save-business', save_business_clicked);
	$('#btn-save-referral').click(save_referral);
	$('#invite_emails').focus(clear_business_addr);

	$('#invite_emails.typeahead').bind('typeahead:select', function(ev, suggestion) {
		var fd = {};
		fd.csrf_token = "{{ csrf_token() }}";
		fd.profile_id = suggestion.id;
		get_profile(fd);
	});

	// https://github.com/twitter/typeahead.js/blob/master/doc/jquery_typeahead.md#custom-events
	$('#invite_emails.typeahead').bind('typeahead:autocompleted', function(ev, suggestion) {
		var fd = {};
		fd.csrf_token = "{{ csrf_token() }}";
		fd.profile_id = suggestion.id;
		console.log('autocompleted');
		get_profile(fd);
	}).bind('typeahead:render', function(evt, suggestions, name) {
		if ($('#profile-card').hasClass('no-display')) {
			$('#not-found').removeClass('no-display');
		} else {
			$('#not-found').addClass('no-display');
		}
	});

	$('#refer-why').keyup(function(evt) {
		txt = $(this).val();
		max	= $(this).attr('maxlength');
		nr	= max - txt.length;
		$('#refer-why-nr').text(nr);
	});

	$('#refer-proj').tagsinput({
		typeaheadjs: {
			name: 'projects',
			displayKey: 'name',
			valueKey: 'name',
			source: projects.ttAdapter()
		}
	});
});
