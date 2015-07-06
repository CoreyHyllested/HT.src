var referral_version = 0.5;

$(document).ready(function () {
	console.log('referral.js: v' + referral_version);

	var pro_finder = new Bloodhound({
		datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
		queryTokenizer: Bloodhound.tokenizers.whitespace,
		remote: {
			url: '/business/search/%QUERY.json',
			wildcard: '%QUERY'
		}
	});



	$('#refer-professional .typeahead').typeahead({
		hint: true,
		highlight: true,
		minLength: 4,
	},
	{
		display: 'name',
		source: pro_finder,
		templates: {
			empty: '<div>We did not find any contractors that matched that query.</div>',
			suggestion: Handlebars.compile('<div class="pro-suggestion" data-id={{id}}>{{name}} <span class="pro-suggestion-addr">{{addr}}</span></div>')
		}
	});
});
