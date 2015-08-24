var forms_version = 0.2;



$(document).ready(function() {
	console.log('forms.js v'+forms_version);
	$('.field.input').blur(function(e) {
		$(this).css('border-color', '#e1e8ed');
	});

});

