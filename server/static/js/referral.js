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
		name: 'coreyisaverytallman',
		display: 'value',
		source: pro_finder,
		templates: {
			empty: [
					'<div class="empty-message">',
					'We did not find any contractors matching that query',
					'</div>'
			].join('\n'),
			suggestion: Handlebars.compile('<div style="width: 100%; height: 20px;"><span style="float: left;">{{value}}</span> <span style="font-size: .9em; color: gray; float: right;">{{addr}}</span></div>')
		}
	});

});
