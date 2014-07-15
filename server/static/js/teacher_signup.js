Dropzone.autoDiscover = false;

$(document).ready(function(){

	// Form Navigation and State Management

	var firstPage = "intro";
	var lastPage = "payment";

	$(document.body).on("click", "#topLeftNavBack", function(e) {
		e.preventDefault();
		window.history.back();	
	});

	if (window.location.hash) {
		var hash = window.location.hash.substring(1);	
		$('#'+hash).show();
		history.replaceState({title: hash}, "", '');
	} else {
		// Default to first page
		$('#'+firstPage).show();
		history.replaceState({title: firstPage}, "", '');
	}

	window.onpopstate = function(event) {
		if (event.state) {
			var page_title = event.state.title;
			$('.ssFormPage').hide();
			$("#"+page_title).show();
		}
	};	

	$('.ssNavItem').click(function() {
		$('.ssFormPage').hide();
		$(".ssNavItem").removeClass("active");
		var target = $(this).attr("data-target-page");
		// $('.ssHeaderPageName').text($("#"+target+' .formTitle').text());
		$("#"+target).show();
		$(this).addClass("active");
		history.pushState({title: target}, "", '/teacher/signup#'+target);
	});

	$('.ssFormButton').click(function(e) {
		e.preventDefault();
		$('.ssFormPage').hide();
		$(".ssNavItem").removeClass("active");
		var currentPage = $(this).attr("data-current-page");
		var nextPage = $('#'+currentPage).next('.ssFormPage').attr("id");
		// $('.ssHeaderPageName').text($('#'+nextPage+' .formTitle').text());
		$('#'+nextPage).show();
		$(".ssNavItem[data-target-page=" + nextPage + "]").addClass("active");
		history.pushState({title: nextPage}, "", '/teacher/signup#'+nextPage);
	});

	$('.ssFormButtonSubmit').click(function(e) {
		e.preventDefault();
		var formData = {};
		formData.oauth_stripe = $("#oauth_stripe").val();
		if ($("#ssAvailOptionFlex").is(":checked")) {
			formData.ssAvailOption = 0;
		} else if ($("#ssAvailOptionSpec").is(":checked")) {
			formData.ssAvailOption = 1;
		}
		formData.ssAvailTimes = "all the time"; // TODO - Change when it matters
		console.log(JSON.stringify(formData));		
		console.log("Photo details: 'ssProfileImage' - "+ JSON.stringify($("#ssProfileImage")[0].files[0]));




		$("#ssForm").submit();

	});

	$('.ssFormPrevious').click(function(e) {
		e.preventDefault();
		$('.ssFormPage').hide();	 
 		$(".ssNavItem").removeClass("active");
		var currentPage = $(this).closest(".ssFormPage").attr("id");
		var prevPage = $('#'+currentPage).prev('.ssFormPage').attr("id");
		console.log("current page is "+currentPage);
		// $('.ssHeaderPageName').text($('#'+prevPage+' .formTitle').text());
		$('#'+prevPage).show();
		$(".ssNavItem[data-target-page=" + prevPage + "]").addClass("active");
		history.pushState({title: prevPage}, "", '/teacher/signup#'+prevPage);
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
			if (width < 720) {
				$(".ssProfileImageInfo").append("<br><span class='error'>Error: Photo must be at least 720 pixels wide.</span>");
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
