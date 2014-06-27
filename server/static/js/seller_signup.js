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

		// var formData = {};
		// formData.ssAddress1 = $("#ssAddress1").val();
		// formData.ssAddress2 = $("#ssAddress2").val();
		// formData.ssCity = $("#ssCity").val();
		// formData.ssState = $("#ssState").val();
		// formData.ssZip = $("#ssZip").val();
		// formData.oauth_stripe = $("#oauth_stripe").val();
		// formData.ssAvailOption = $("#ssAvailOption").val();
		// formData.ssAvailTimes = $("#ssAvailTimes").val();

		// console.log(JSON.stringify(formData));

		$('.ssFormPage').hide();

		var currentPage = $(this).attr("data-current-page");
		var nextPage = $('#'+currentPage).next('.ssFormPage').attr("id");

		// $('.ssHeaderPageName').text($('#'+nextPage+' .formTitle').text());
		$('#ssFormButton').attr("data-current-page", nextPage);
		$('.ssFormPrevious').show();
		$('#'+nextPage).show();
	});

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

	/* When visible 'Choose File...' is clicked, activate hidden 'Browse...' */
	$("#ssProfileImageButton").click(function() {
   		$("#ssProfileImage").click();
	});

	$("#ssProfileImage").change(function(e) {
		createReader(this, function(width, height) {
			$(".ssProfileImageInfo").html("Height: "+height+"px, Width: "+width+"px");
			// Add more size checks here if desired
			if (height > width) {
				$(".ssProfileImageInfo").append("<br><span class='error'>Error: Photo is not in landscape orientation.</span>");
			}			
			if (width < 800) {
				$(".ssProfileImageInfo").append("<br><span class='error'>Error: Photo must be at least 800 pixels wide.</span>");
			}
		});		
	});

});

function createReader(input, whenReady) {

	if (input.files && input.files[0]) {
		var reader = new FileReader();
		reader.onload = function (e) {
		    var image = new Image;
		    image.onload = function(e) {
	            var width = this.width;
	            var height = this.height;
	            var src = this.src;
	            if (whenReady) whenReady(width, height, src);
		    };
		    image.src = e.target.result;
		    $('.ssUploadPreviewImage').attr('src', e.target.result).show();
		}
		reader.readAsDataURL(input.files[0]);

	}

}

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
