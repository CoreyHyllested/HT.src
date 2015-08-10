var referral_version = 0.83;

function clear_referral() { $('#rid').val(''); }
function clear_profile() {
	if (!$('#trusted').attr('readonly')) {
		$('#trust-card').addClass('no-display');
		$('#instructions').addClass('no-display');
		$('#not-found').removeClass('no-display');
	}
}


function business_submit(event) {
	// runs when form is valid (on Chrome).
	event.preventDefault();	//prevent submit.

	if (!$(event.target).hasClass('update')) {
		return business_update(event);
	}

	business_create(event);
	return false;
}

function business_update(event) {
	$(event.target).toggleClass('update');
	$('#modal-business-info').toggleClass('block');
	$('#modal-business-addr').toggleClass('block');
	$('#modal-message button[type="submit"]').html('Submit');
	initialize_map('modal-map', 'address-search');
	return false;
}


function business_create(event) {
	console.log('POST business info', event);

	fd = new FormData();
	fd.append("csrf_token", $('#csrf_token').val());
	fd.append("name", $('#trusted').val());
	fd.append("addr", geocode_address($('#address-search').val()));
	fd.append("site", $('#site').val());
	fd.append("email", $('#email').val());
	fd.append("phone", $('#phone').val());

	console.log($('#trusted').val());
	console.log(fd);
	$.ajax({ url	: '/business/create',
			type	: "POST",
			data	: fd,
			processData: false,
			contentType: false,
			success : function(response) {
				shut_modal_window();

				var profile_fd = {};
				profile_fd.csrf_token = $('#csrf_token').val(),
				profile_fd.profile_id = response.business.business_id;
				get_profile(profile_fd);
				positive_feedback('Added ' + response.business.business_name);
			},
			error	: function(xhr, status, error) {
				console.log("AJAX Error", xhr);
				if (xhr.status == 400) {
					// form error(s) occurred.
					$('#modal-business-info').addClass('block');
					$('#modal-business-addr').removeClass('block');
					show_errors('#modal-message .action-feedback', xhr.responseText);
				} else if (xhr.status == 401) {
					console.log('GET login-modal');
					//window.location.href = '/login';
					openAlertWindow('You must login first');
				} else { }
			}
	});
}


function save_referral(evt) {
	$(".action-feedback").html("Saving...").fadeIn();

	rid	= $('#rid').val();
 	fd	= new FormData($('#refer-form')[0])

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
					set_status('.action-feedback', 'Saved');
				},
				error	: function(xhr) {
					console.log("AJAX Error");
					if (xhr.status == 400) {
						// form error(s) occurred.
						$('#modal-business-info').addClass('block');
						$('#modal-business-addr').removeClass('block');
						show_errors('.action-feedback', xhr.responseText);
					} else if (xhr.status == 401) {
						//  xhr.status is 401, redirectiing user to authenticate.
						//  todo: we should pop-up a login/signup modal instead.
						openAlertWindow('You must login first');
						//window.location.href = '/login';
					}
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

project_ctx = new Bloodhound({
	datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
	queryTokenizer: Bloodhound.tokenizers.whitespace,
	prefetch: {
	url: "/context.json",
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
					$('#not-found').addClass('no-display');
					$('#instructions').removeClass('no-display');

					busname = data.business_name
					if (data.business_website) {
						busname = '<a href="' + data.business_website + '" target="_blank">' + busname + '</a>'
					}
					$('#pro-name').html(busname);
					/* examples of setting phone, email in git-log (july-21-15) */
					$('#bid').val(fd.profile_id);
					$('#content').focus();
				},
				error	: function(data) {
					console.log("AJAX Error");
				}
	});
}


function clear_business_addr( event ) {
	if ($('#trusted').attr('readonly')) return;

	trusted = $('#trusted').val();
	bar_idx = trusted.lastIndexOf(" | ");
	if (bar_idx == -1) return;
	$('#trusted').val(trusted.substring(0, bar_idx));
}




$(document).ready(function () {
	console.log('referral.js: v' + referral_version);

	$('#refer-form .typeahead').typeahead({
		hint: true,
		highlight: true,
		minLength: 4,
	},
	{
		display: 'combined',
		source: pro_finder,
		templates: {
			notFound: function(q) {
				return '<div id=\'not-found\'>We did not match \"' + q.query + '\".<br><a href="javascript:add_new_business();">Add this business?</a></div>';
			},
			pending: '<div>Searching...</div>',
			suggestion: Handlebars.compile('<div class="pro-suggestion" data-id={{id}}>{{name}} <span class="pro-suggestion-addr">{{addr}}</span></div>')
		}
	});

	project_ctx.initialize();

	$('#trusted').focus(clear_business_addr);
	$('#trusted').keydown(clear_profile);

	$('#btn-cancel-referral').click( function (e) { clear_profile(); });
	$('#btn-submit-referral').click( function (e) { save_referral(); });
	$('#modal-message').on('submit', '#create-business-form', business_submit);

	$('#trusted.typeahead').bind('typeahead:select', function(ev, suggestion) {
		var fd = {};
		fd.csrf_token = $('#csrf_token').val();
		fd.profile_id = suggestion.id;
		get_profile(fd);
	});

	// https://github.com/twitter/typeahead.js/blob/master/doc/jquery_typeahead.md#custom-events
	$('#trusted.typeahead').bind('typeahead:autocompleted', function(ev, suggestion) {
		var fd = {};
		fd.csrf_token = $('#csrf_token').val();
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

	$('#content').on('focus', function() { clear_error_box(this); });
	$('#content').on('blur',  function() { clear_error_msg(this); });
	$('#content').keyup(function(evt) {
		txt = $(this).val();
		max	= $(this).attr('maxlength');
		$('#content-nr').text('(' + (max - txt.length) + ' chars left)');
	});

	$('#context').tagsinput({
		typeaheadjs: {
			name: 'context',
			displayKey: 'name',
			valueKey: 'name',
			source: project_ctx.ttAdapter()
		}
	});
});
