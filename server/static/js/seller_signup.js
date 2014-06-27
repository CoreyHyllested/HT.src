Dropzone.autoDiscover = false;

$(document).ready(function(){

	// Default to first page
	var firstPage = "ssFormAddress";

	// $('.ssHeaderPageName').text($('#'+firstPage+' .formTitle').text());
	$('#'+firstPage).show();
	$('#ssFormButton').attr("data-current-page", firstPage);

	$('.ssNavLink').click(function() {
		$('.ssFormPage').hide();
		var target = $(this).attr("data-target-page");
		$('.ssHeaderPageName').text($("#"+target+' .formTitle').text());
		$('#ssFormButton').attr("data-current-page", target);

		if (target != firstPage) {
			$('.ssFormPrevious').show();
		} else {
			$('.ssFormPrevious').hide();
		}

		$("#"+target).show();
	});

	$('#ssFormButton').click(function(e) {
		e.preventDefault();
		$('.ssFormPage').hide();

		var currentPage = $(this).attr("data-current-page");
		var nextPage = $('#'+currentPage).next('.ssFormPage').attr("id");

		// $('.ssHeaderPageName').text($('#'+nextPage+' .formTitle').text());
		$('#ssFormButton').attr("data-current-page", nextPage);
		$('.ssFormPrevious').show();
		$('#'+nextPage).show();
	})

	$('#ssFormPrevious').click(function(e) {
		e.preventDefault();
		$('.ssFormPage').hide();	

		var currentPage = $(this).siblings('#ssFormButton').attr("data-current-page");
		console.log("currentPage is "+ currentPage);

		var prevPage = $('#'+currentPage).prev('.ssFormPage').attr("id");
		console.log("prevPage is "+ prevPage);

		// $('.ssHeaderPageName').text($('#'+prevPage+' .formTitle').text());
		$('#ssFormButton').attr("data-current-page", prevPage);
		if (prevPage != firstPage) {
			$('.ssFormPrevious').show();
		} else {
			$('.ssFormPrevious').hide();
		}		
		$('#'+prevPage).show();
	})


	// mydropzone = new Dropzone("form.dropzone", 
	// 	{ 
	// 		url: '/upload',
	// 		parallelUploads: 100,
	// 		uploadMultiple: true,
	// 		addRemoveLinks: true,
	// 		maxFiles: 1,
	// 		maxFileSize: 4,
	// 		acceptedFiles: "image/*",
	// 		autoProcessQueue: false,
	// 		clickable: true,
	// 		thumbnailHeight: 400,
	// 		previewsContainer: ".dropzone-previews"
	// 	}
	// );


	// mydropzone.on("errormultiple", function(file, errorMessage) {
	// 	$(".dropzone-status").html("<span class='error'>Error Encountered: "+errorMessage+"</span>");
	// });

	// mydropzone.on("successmultiple", function(file) {
	// 	$(".dropzone-status").html("<span class='success'>Image successfully uploaded. </span>");
	// });

	// mydropzone.on("processing", function() {
	// 	this.options.autoProcessQueue = true;
	// });

	// $('button.uploadButton').click(function() {
	// 	mydropzone.processQueue();
	// });


	// $('button.ssFormButton').attr("disabled", true);
	$('button.ssFormButton').click(function() {
		validateForm();
	});

});

function validateForm() {
	// Fetch form elements
	var address1 = document.forms["ssForm"]["ssAddress1"];

	// Check for empty fields; if found, highlight them
	var form_fields = [address1];
	for (var i = 0; i < form_fields.length; i++) {
		var current_element = form_fields[i];
		var current_value = form_fields[i].value;
		if (current_value.match(/^\s*$/)) {
			$(current_element).focus();
			return false;
		}
	}
}

function submitForm() {
	// Fetch form elements
	var address1 = document.forms["ssForm"]["ssAddress1"];

	// Assemble an object

	// Do an ajax insert, target add_seller_info




}
