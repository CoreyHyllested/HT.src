var referral_version = 0.97;


function clear_referral() { $('#rid').val(''); }
function clear_profile() {
	if (!$('#trusted').attr('readonly')) {
		$('#trust-card').addClass('no-display');
		$('#trust-badge').html('');
		$('.linkto-referral').html('');
		//$('#instructions').addClass('no-display');
		$('#not-found').removeClass('no-display');
	}
}


function add_new_business() {
	fd = {};
	fd.name = $('#trusted').val();
	fd.csrf_token = $('#csrf_token').val();

	console.log('add new business ' + fd.name);
	$.ajax({type	: 'GET',
			url		: '/business/new',
			data	: fd,
			contentType: false,
			success : function(response) {
				console.log(response);
				open_task_window(response.embed);
				$('#phone').mask("(999) 999-9999");
			},
			error	: function(xhr, status, error) {
				console.log(['ajax error', xhr]);
				if (status == 401) { window.location.href = '/login'; }
			}
	});
	return false;
}


function business_submit(event) {
	// runs when form is valid (on Chrome).
	event.preventDefault();	//prevent submit.

	if (!$(event.target).hasClass('update')) {
		return business_update(event);
	}

	p = geocode_address( $('#address-search').val() );
	p.always(business_create);
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



function business_create() {
	fd	= new FormData($('#create-business-form')[0])
	$.ajax({ url	: '/api/business/create',
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
				if (xhr.status === 400) {
					// form error(s) occurred.
					$('#modal-business-info').addClass('block');
					$('#modal-business-addr').removeClass('block');
					show_errors('#modal-message .action-feedback', xhr.responseJSON);
				} else if (xhr.status === 401) {
					open_login(xhr.status);
				} else { }
			}
	});
}


function referral_remove() {
	$('#trusted').val('');
	$('#content').val('');
	$('span.tag.label').remove();
	$('.bootstrap-tagsinput input.tt-input').val('');
	$('#form-referral .typeahead').typeahead('val', '');
	$('#btn-cancel-referral').val('CLEAR');
	clear_profile();
}


function referral_submit(event) {
	event.preventDefault();

	set_status('.action-feedback', 'Saving...');
	unsaved = $('.bootstrap-tagsinput input.tt-input');
	$('#context').tagsinput('add', unsaved.val());

	fd	= new FormData( $('#form-referral')[0] );

	rid	= $('#rid').val();
	uri	= "/api/referral/create";
	if (rid) { uri = "/api/referral/" + rid + "/update"; }

	$.ajax({	url		: uri,
				type	: "POST",
				data	: fd,
				processData: false,
				contentType: false,
				success : function(xhr) {
					$('#rid').val(xhr.ref_uuid);
					$('.linkto-referral').html('Your <a href="/profile?hlr=' + xhr.ref_uuid + '">Referral</a>');
					$('#btn-cancel-referral').val('Write Another');
					set_status('.action-feedback', 'Saved');
				},
				error	: function(xhr, status, error) {
					if (xhr.status === 401) {
						open_login(xhr.status);
					} else if (xhr.status === 400) {
						// form error(s) occurred.
						show_errors('.action-feedback', xhr.responseJSON);
					} else if (xhr.status === 500) {
						show_errors('.action-feedback', xhr.responseJSON);
					} else {
						console.log('Missing response for error', xhr.status);
					}
				}
	});
	return false;
}

pro_finder = new Bloodhound({
	datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
	queryTokenizer: Bloodhound.tokenizers.whitespace,
	remote: {
		url: '/api/business/search/%QUERY',
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


function busapi_get_breadcrumbs(categories) {
	if (categories.length === 0) {
		return '';
	}

	breadcrumbs = '';
	categories.forEach(function (elem, idx) {
		crumb = elem;
		console.log(idx, elem, (idx < categories.length - 1));
		if (idx < categories.length - 1) {
			crumb = crumb + ' &raquo; ';
		}
		breadcrumbs = breadcrumbs + crumb;
	});

	return breadcrumbs;
}


function busapi_get_emails(email) {
	if (!email) return '';
	return '<a href="mailto:' + email + '" target="_blank" title="' + email + '"><i class="fa fa-envelope-o"></i></a>';
}


function trustcard_append_badge(embed_html, inline) {
	if (embed_html === '') return;
	$badges = $('#trust-badge');

	li = document.createElement('li');
	if (inline) $(li).addClass('inline');

	$(li).html(embed_html);
	$badges.append(li);
}



function get_profile(fd) {
	clear_referral();
	$.ajax({type	: "POST",
			url		: "/api/business/" + fd.profile_id,
			data	: fd,
			success : function(xhr) {
				console.log(xhr);
				$('#trust-card').removeClass('no-display');
				$('#trust-card').attr('data-id', fd.profile_id);
				$('#not-found').addClass('no-display');

				categories = busapi_get_breadcrumbs(xhr.business_category[0]);
				trustcard_append_badge(categories, false);

				if (xhr.business_website) {
					busname = '<a href="' + xhr.business_website + '" target="_blank">' + xhr.business_name + '</a>'
					website = '<a href="' + xhr.business_website + '" target="_blank" title="Website"><i class="fa fa-link"></i></a>';
					trustcard_append_badge(website, true);
				}

				if (xhr.address) {
					addrurl = 'https://www.google.com/maps/place/' + xhr.address;
					address = '<a href="' + addrurl + '" target="_blank" title="' + xhr.address + '"><i class="fa fa-map-marker"></i></a>'
					trustcard_append_badge(address, true);
				};

				email = busapi_get_emails(xhr.business_emails[0]);
				trustcard_append_badge(email, true);

				xhr.business_phones.forEach(function (elem, idx) {
					phone = '<a href="tel:' + elem + '" title="' + elem + '"><i class="fa fa-phone"></i></a>'
					trustcard_append_badge(phone, true);
				});

				
				folder = '<a href="/business/' + xhr.business_id + '" target="_blank" title="Referrals for ' + xhr.business_name + '"><i class="fa fa-folder-open"></i></a>'
				trustcard_append_badge(folder, true);

				$('#pro-name').html(xhr.business_name);
				$('#trusted').val(xhr.business_name);	// user may have updated name.
				$('#content').focus();
				$('#bid').val(fd.profile_id);
			},
			error	: function(xhr, status, error) {
				console.log("AJAX Error", xhr);
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

	$('#form-referral .typeahead').typeahead({
		hint: true,
		highlight: true,
		minLength: 3,
	},
	{
		display: 'combined',
		source: pro_finder,
		limit: 100,		//https://github.com/twitter/typeahead.js/issues/1232
		templates: {
			notFound: function(q) {
				return '<div id="not-found">We did not match "' + q.query + '". &nbsp; <a href="javascript:add_new_business();">Add this business?</a></div>';
			},
			pending: '<div>Searching...</div>',
			suggestion: Handlebars.compile('<div class="pro-suggestion" data-id={{id}}>{{name}} <span class="pro-suggestion-addr">{{addr}}</span></div>')
		}
	});

	project_ctx.initialize();

	$('#trusted').focus(clear_business_addr);
	$('#trusted').keydown(clear_profile);

	$('#btn-cancel-referral').on('click', referral_remove);
	$('#form-referral').on('submit', referral_submit);
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

	$('#referral-questions').on('focusin',  'div.bootstrap-tagsinput', function() { $(this).addClass(    'active' ); });
	$('#referral-questions').on('focusout', 'div.bootstrap-tagsinput', function() {	$(this).removeClass( 'active' ); });
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
