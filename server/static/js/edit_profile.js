$(document).ready(function() {

	// Form Navigation and State Management

	var firstPage = "general";
	var lastPage = "payment";
	var path = "/profile/edit";

	$(document.body).on("click", "#topLeftNavBack", function(e) {
		e.preventDefault();
		// window.history.back();	
		document.location.href = "/profile";
	});

	if (window.location.hash) {
		$(".editProfNavItem").removeClass("active");
		var hash = window.location.hash.substring(1);
		$('#'+hash).show();
		var currentNav = $(".editProfNavItem[data-target-page=" + hash + "]");
		history.replaceState({title: hash}, "", '');
	} else {
		// Default to first page
		$('#'+firstPage).show();
		var currentNav = $(".editProfNavItem[data-target-page=" + firstPage + "]");
		history.replaceState({title: firstPage}, "", '');
	}
	currentNav.addClass("active");
	$('.editProfHeaderPageName').text(currentNav.text());

	window.onpopstate = function(event) {
		if (event.state) {
			var page_title = event.state.title;
			$('.editProfFormPage').hide();
			$("#"+page_title).show();
		}
	};	

	$('.editProfNavItem').click(function() {
		$('.editProfFormPage').hide();
		$(".editProfNavItem").removeClass("active");
		var target = $(this).attr("data-target-page");
		$('.editProfHeaderPageName').text($(this).text());
		$("#"+target).show();
		$(this).addClass("active");
		history.pushState({title: target}, "", path+'#'+target);
	});

	$('.editProfFormButton').click(function(e) {
		e.preventDefault();
		$('.editProfFormPage').hide();
		$(".editProfNavItem").removeClass("active");
		var currentPage = $(this).attr("data-current-page");
		var nextPage = $('#'+currentPage).next('.editProfFormPage').attr("id");
		var nextNav = $(".editProfNavItem[data-target-page=" + nextPage + "]");
		$('.editProfHeaderPageName').text(nextNav.text());
		$('#'+nextPage).show();
		$(".editProfNavItem[data-target-page=" + nextPage + "]").addClass("active");
		history.pushState({title: nextPage}, "", path+'#'+nextPage);
	});

	$('.editProfFormButtonSubmit').click(function(e) {
		e.preventDefault();
		var formData = {};
		// formData.oauth_stripe = $("#oauth_stripe").val();

		console.log(JSON.stringify(formData));		
		console.log("Photo details: 'editProfImage' - "+ JSON.stringify($("#editProfImage")[0].files[0]));

		$("#editProfForm").submit();

		// TODO - Make it AJAX

	});

	$('.editProfFormPrevious').click(function(e) {
		e.preventDefault();
		$('.editProfFormPage').hide();	 
 		$(".editProfNavItem").removeClass("active");
		var currentPage = $(this).closest(".editProfFormPage").attr("id");
		var prevPage = $('#'+currentPage).prev('.editProfFormPage').attr("id");
		var prevNav = $(".editProfNavItem[data-target-page=" + prevPage + "]");
		$('.editProfHeaderPageName').text(prevNav.text());
		$('#'+prevPage).show();
		$(".editProfNavItem[data-target-page=" + prevPage + "]").addClass("active");
		history.pushState({title: prevPage}, "", path+'#'+prevPage);
	})



	// /* When visible 'Choose File...' is clicked, activate hidden 'Browse...' */
	// $("#editProfChooseImage").click(function() {
 //   		$("#change-photo-button").click();
	// });


	// /* When the profile pic is clicked, activate hidden 'Browse...' */
	// $("#editProfImagePreview").click(function() {
 //   		$("#change-photo-button").click();
	// });

	$(".editProfSave").click(function(e) {
		e.preventDefault();
		saveProfile();
	});


	// Image Upload

	/* When visible 'Choose Image...' or the preview image is clicked, activate hidden 'Browse...' */
	$("#editProfImageButton, #editProfImagePreview").click(function() {
   		$("#editProfImage").click();
	});

	$("#editProfImage").change(function(e) {
		createReader(this, function(width, height) {
			$(".editProfImageInfo").html("Height: "+height+"px, Width: "+width+"px");
			// Add more size checks here if desired
			if (height > width) {
				$(".editProfImageInfo").append("<br><span class='error'>Error: Photo is not in landscape orientation.</span>");
			}			
			if (width < 720) {
				$(".editProfImageInfo").append("<br><span class='error'>Error: Photo must be at least 720 pixels wide.</span>");
			}
		});		
	});

	// Old Image Stuff

	$('#change-photo-button').change(function(e) {
		reloadProfImg("/static/img/loader.GIF", true, false);
		
		var fd = new FormData($('#editform')[0]);
		fd.append('csrf_token', $('#csrf_token').val());
		fd.append('profile', true);

		var xhr = new XMLHttpRequest();
		if ( xhr.upload ) {
			xhr.upload.onprogress = function(e) {
				var done = e.position || e.loaded, total = e.totalSize || e.total;
				console.log('xhr.upload progress: ' + done + ' / ' + total + ' = ' + (Math.floor(done/total*1000)/10) + '%');
			};
		}

		xhr.onreadystatechange = function(e) {
		if (4 == this.readyState) {
				console.log(['xhr upload complete', e]);
				rc = JSON.parse(xhr.responseText);
				console.log(xhr.responseText);
				reloadProfImg(rc['tmp'], false, true);
			}
		};
		xhr.open('post', "/upload", true);
		xhr.send(fd);
		return false;
	});

	function reloadProfImg(url, loader, uploaded) {
		$("#profile_img").attr("src", url);
		if (loader) {
			$("#profile_img").height(80).width(80);
			$("#profile_img").css('margin-left',90+'px');
			$("#profile_img").css('margin-top',20+'px');
		}
		if (uploaded) {
			$("#profile_img").height(151).width(269);
			$("#profile_img").css('margin-left',0);
			$("#profile_img").css('margin-top',0);
		}
	}

	// Form element behavior


	$("#editProfAvailTimes").css("opacity", .4).attr("disabled", "disabled");

	if ($('#edit_availability').val() == "2") {
		$("#editProfAvailTimes").css("opacity", 1).removeAttr("disabled");
	}


	$('#edit_availability').change(function() {
		if ($(this).val() == "2") {
		  $("#editProfAvailTimes").css("opacity", 1).removeAttr("disabled");
		} else {
		  $("#editProfAvailTimes").css("opacity", .4).attr("disabled", "disabled");
		} 
	});		


	$(".timeSelector").css("opacity", .4).attr("disabled", "disabled");

	// When loading form - activate times when date is selected
	// $.each(".daySelector", function() {


	// });

	$(".daySelector").change(function() {
		if ($(this).prop("checked")) {
		  $(this).siblings(".timeSelector").css("opacity", 1).removeAttr("disabled");
		} else {
		  $(this).siblings(".timeSelector").css("opacity", .4).attr("disabled", "disabled");
		} 		
	})

});


function saveProfile() {

	var fd = new FormData($('#editProfForm')[0]);

	$(".editProfFormStatus").html("Saving...").fadeIn();

	$.ajax({ url	: "/profile/update",
			type	: "POST",
			data : fd,
			processData: false,
  			contentType: false,
			success : function(response) {

			 	console.log("AJAX Success - profile saved.");

			 	// openAlertWindow("Success: " + response.usrmsg);			 	

			 	var imageInput = "#editProfImage";
			 	$(imageInput).wrap('<form>').closest('form').get(0).reset();
				$(imageInput).unwrap();

			 	$(".editProfFormStatus").html("<span class='success'>Changes Saved.</span>").fadeIn(400);
				setTimeout(function() {
					$('.editProfFormStatus').fadeOut(400);
				}, 1600 );
			}, 
			error: function(xhr, status, error) {
				console.log("AJAX Error - profile not saved.");

				var err = JSON.parse(xhr.responseText);
				var errors = err.errors;
				
				console.log("FORM ERRORS:");
				console.log(JSON.stringify(errors));

				$(".editProfFormStatus").html("<span class='error'>");
				$.each(errors, function(i, v) {
					$(".editProfFormStatus").append(i+": "+v);
				});
				$(".editProfFormStatus").append('</span>').fadeIn();

				openAlertWindow("Error: " + err.usrmsg);
				// $(".lessonFormStatus").html("<span class='error'>Sorry, something went wrong. Lesson not saved.</span>").fadeIn();
			
			}
	});
	return false;

}


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
		    $('.editProfImagePreview').attr('src', e.target.result).show();
		}
		reader.readAsDataURL(input.files[0]);

	}

}
