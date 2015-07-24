var referral_version = 0.63;

function clear_referral() { $('#rid').val(''); }
function clear_profile() {
	$('#trust-card').addClass('no-display');
	$('#instructions').addClass('no-display');
}


function save_business_clicked() {
	fd = new FormData();
	fd.append("csrf_token", $('#csrf_token').val());
	fd.append("name", $('#name').val());
	fd.append("site", $('#site').val());
	fd.append("email", $('#email').val());
	fd.append("phone", $('#phone').val());
	create_business(fd);
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
				console.log(['ajax error', xhr]);
				if (status == 401) { window.location.href = '/login'; }
				rc = JSON.parse(xhr.responseText);
			}
	});
	return false;
}


function create_business(fd) {
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
				profile_fd.csrf_token = $('#csrf_token').val(),
				profile_fd.profile_id = response.business.business_id;
				get_profile(profile_fd);
				add_feedback('Added ' + response.business.business_name);
			},
			error	: function(data) {
				console.log("AJAX Error");
				if (status == 401) { window.location.href = '/login'; }
				console.log(data);
			}
	});
}


function save_referral(evt) {
	rid	= $('#rid').val();
 	fd	= new FormData($('#refer-form')[0])
	fd.append("csrf_token", $('#csrf_token').val());

	// create or update referral.
	referral_uri = "/referral/create";
	if (rid != '') { referral_uri = "/referral/" + rid + "/update"; }

	$.ajax({	url		: referral_uri,
				type	: "POST",
				data	: fd,
				processData: false,
				contentType: false,
				success : function(data) {
					$('#rid').val(data.ref_uuid);
					add_feedback('Saved');
				},
				error	: function(data) {
					console.log("AJAX Error");
					//  data.status is 401, redirectiing user to authenticate.
					//  todo: we should pop-up a login/signup modal instead.
					if (data.status == 401) { window.location.href = '/login'; }
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
	clear_referral();
	$.ajax({	url		: "/business/" + fd.profile_id,
				type	: "GET",
				data	: fd,
				success : function(data) {
					$('#trust-card').removeClass('no-display');
					$('#trust-card').attr('data-id', fd.profile_id);
					$('#instructions').removeClass('no-display');

					busname = data.business_name
					if (data.business_website) {
						busname = '<a href="' + data.business_website + '" target="_blank">' + busname + '</a>'
					}
					$('#pro-name').html(busname);
					/* examples of setting phone, email in git-log (july-21-15) */
					$('#content').focus();
					$('#bid').val(fd.profile_id);
				},
				error	: function(data) {
					console.log("AJAX Error");
				}
	});
}


function clear_business_addr( event ) {
	name = $('#trusted').val();
	idx = name.lastIndexOf(" | ")
	if (idx == -1) { return; }
	strng = name.substring(0, name.lastIndexOf(" | "));
	$('#trusted').val(strng);
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

	$('#trusted').focus(clear_business_addr);
	$('#trusted').keydown(clear_profile);

	$('#btn-cancel-referral').click( function (e) { clear_profile(); });
	$('#btn-submit-referral').click( function (e) { save_referral(); });
	$('#modal-buttons').on('click', '.save-business', save_business_clicked);

	$('#trusted.typeahead').bind('typeahead:select', function(ev, suggestion) {
		var fd = {};
		fd.csrf_token = "{{ csrf_token() }}";
		fd.profile_id = suggestion.id;
		get_profile(fd);
	});

	// https://github.com/twitter/typeahead.js/blob/master/doc/jquery_typeahead.md#custom-events
	$('#trusted.typeahead').bind('typeahead:autocompleted', function(ev, suggestion) {
		var fd = {};
		fd.csrf_token = "{{ csrf_token() }}";
		fd.profile_id = suggestion.id;
		console.log('autocompleted');
		get_profile(fd);
	}).bind('typeahead:render', function(evt, suggestions, name) {
		if ($('#trust-card').hasClass('no-display')) {
			$('#not-found').removeClass('no-display');
		} else {
			$('#not-found').addClass('no-display');
		}
	});

	$('#content').keyup(function(evt) {
		txt = $(this).val();
		max	= $(this).attr('maxlength');
		nr	= max - txt.length;
		$('#content-nr').text(nr);
	});

	$('#context').tagsinput({
		typeaheadjs: {
			name: 'projects',
			displayKey: 'name',
			valueKey: 'name',
			source: projects.ttAdapter()
		}
	});
});
