Dropzone.autoDiscover = false;

$(document).ready(function(){

	// Form Navigation and State Management

	var firstPage = "profile_photo";
	var lastPage = "schedule";

	$(document.body).on("click", "#topLeftNavBack", function(e) {
		e.preventDefault();
		window.history.back();	
	});

	if (window.location.hash) {
		var hash = window.location.hash.substring(1);
		if (hash == lastPage) {
			$('#ssFormButton').hide();
			$('#ssFormButtonSubmit').show();
		} else {
			$('#ssFormButton').show();
			$('#ssFormButtonSubmit').hide();			
		}		
		$('#'+hash).show();
		$('#ssFormButton').attr("data-current-page", hash);
		history.replaceState({title: hash}, "", '');
	} else {
		// Default to first page
		$('#'+firstPage).show();
		$('#ssFormButton').attr("data-current-page", firstPage);
		history.replaceState({title: firstPage}, "", '');
	}

	window.onpopstate = function(event) {
		if (event.state) {
			var page_title = event.state.title;
			$('.ssFormPage').hide();
			$("#"+page_title).show();
		}
	};	

	$('.ssNavLink').click(function() {
		$('.ssFormPage').hide();
		var target = $(this).attr("data-target-page");
		// $('.ssHeaderPageName').text($("#"+target+' .formTitle').text());
		$('#ssFormButton').attr("data-current-page", target);

		if (target != firstPage) {
			$('.ssFormPrevious').show();
		} else {
			$('.ssFormPrevious').hide();
		}
		if (target == lastPage) {
			$('#ssFormButton').hide();
			$('#ssFormButtonSubmit').show();
		} else {
			$('#ssFormButton').show();
			$('#ssFormButtonSubmit').hide();			
		}

		$("#"+target).show();
		history.pushState({title: target}, "", '/seller_signup#'+target);
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

		if (nextPage == lastPage) {
			$('#ssFormButton').hide();
			$('#ssFormButtonSubmit').show();
		}

		history.pushState({title: nextPage}, "", '/seller_signup#'+nextPage);
	});



	$('#ssFormButtonSubmit').click(function(e) {
		e.preventDefault();
		var formData = {};
		formData.oauth_stripe = $("#oauth_stripe").val();
		formData.ssAvailOption = $("#ssAvailOption").val();
		formData.ssAvailTimes = $("#ssAvailTimes").val();
		console.log(JSON.stringify(formData));		
		console.log("Photo details: 'ssProfileImage' - "+ JSON.stringify($("#ssProfileImage")[0].files[0]));

		// Uncomment when ready to actually do the database stuff
		$("#ssForm").submit();

		openAlertWindow("Thanks for registering!");
	});



	$('#ssFormPrevious').click(function(e) {
		e.preventDefault();
		$('.ssFormPage, #ssFormButtonSubmit').hide();	
		$('#ssFormButton').show();

		var currentPage = $(this).siblings('#ssFormButton').attr("data-current-page");
		var prevPage = $('#'+currentPage).prev('.ssFormPage').attr("id");

		// $('.ssHeaderPageName').text($('#'+prevPage+' .formTitle').text());
		$('#ssFormButton').attr("data-current-page", prevPage);
		if (prevPage != firstPage) {
			$('.ssFormPrevious').show();
		} else {
			$('.ssFormPrevious').hide();
		}
			
		$('#'+prevPage).show();
		history.pushState({title: prevPage}, "", '/seller_signup#'+prevPage);
	})

	// Image Upload

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
