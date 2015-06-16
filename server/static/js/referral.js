var referral_version = 0.5;

$(document).ready(function () {
	console.log('referral.js: v' + referral_version);

	var pro_finder = new Bloodhound({
		datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
		queryTokenizer: Bloodhound.tokenizers.whitespace,
		remote: {
			url: '/professional/search/%QUERY.json',
			wildcard: '%QUERY'
		}
	});



	$('#refer_a_pro .typeahead').typeahead({
		hint: true,
		highlight: true,
		minLength: 4,
	},
	{
		display: 'name',
		source: pro_finder,
		templates: {
			empty: '<div class="empty-message">We did not find any contractors matching that query</div>',
			suggestion: Handlebars.compile('<div style="width: 100%; height: 20px;" data-id={{id}}><span style="float: left;">{{name}}</span> <span style="font-size: .9em; color: gray; float: right;">{{addr}}</span></div>')
		}
	});

});
