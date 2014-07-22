$(document).ready(function() {

	// Form Navigation and State Management

	var firstPage = "general";
	var lastPage = "temp";
	var path = "/profile/edit";

	$(document.body).on("click", "#topLeftNavBack", function(e) {
		e.preventDefault();
		// window.history.back();	
		document.location.href = "/profile";
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
			$('.editProfFormPage').hide();
			$("#"+page_title).show();
		}
	};	

	$('.editProfNavItem').click(function() {
		$('.editProfFormPage').hide();
		$(".editProfNavItem").removeClass("active");
		var target = $(this).attr("data-target-page");
		// $('.editProfHeaderPageName').text($("#"+target+' .formTitle').text());
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
		// $('.editProfHeaderPageName').text($('#'+nextPage+' .formTitle').text());
		$('#'+nextPage).show();
		$(".editProfNavItem[data-target-page=" + nextPage + "]").addClass("active");
		history.pushState({title: nextPage}, "", path+'#'+nextPage);
	});

	$('.editProfFormButtonSubmit').click(function(e) {
		e.preventDefault();
		var formData = {};
		formData.oauth_stripe = $("#oauth_stripe").val();
		if ($("#editProfAvailOptionFlex").is(":checked")) {
			formData.editProfAvailOption = 0;
		} else if ($("#editProfAvailOptionSpec").is(":checked")) {
			formData.editProfAvailOption = 1;
		}
		formData.editProfAvailTimes = "all the time"; // TODO - Change when it matters
		console.log(JSON.stringify(formData));		
		console.log("Photo details: 'editProfImage' - "+ JSON.stringify($("#editProfImage")[0].files[0]));

		$("#editProfForm").submit();

	});

	$('.editProfFormPrevious').click(function(e) {
		e.preventDefault();
		$('.editProfFormPage').hide();	 
 		$(".editProfNavItem").removeClass("active");
		var currentPage = $(this).closest(".editProfFormPage").attr("id");
		var prevPage = $('#'+currentPage).prev('.editProfFormPage').attr("id");
		console.log("current page is "+currentPage);
		// $('.editProfHeaderPageName').text($('#'+prevPage+' .formTitle').text());
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

	/* When visible 'Choose File...' is clicked, activate hidden 'Browse...' */
	$("#editProfImageButton").click(function() {
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

	// Old Stuff

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

});


function saveProfile() {

	var fd = new FormData($('#editProfileForm')[0]);

	$.ajax({ url	: "/profile/update",
			type	: "POST",
			data : fd,
			processData: false,
  			contentType: false,
			success : function(response) {
			 	console.log("AJAX Success - profile saved.");

			 	openAlertWindow("Success: " + response.usrmsg);

			 	// $(".lessonFormStatus").html("<span class='success'>Lesson saved.</span>").fadeIn();
				// setTimeout(function() {
				// 	$('.lessonFormStatus').fadeOut(1000);
				// }, 2000 );
			}, 
			error: function(xhr, status, error) {
				console.log("AJAX Error - profile not saved.");

				var err = JSON.parse(xhr.responseText);
				var errors = err.errors;
				
				console.log("FORM ERRORS:");
				console.log(JSON.stringify(errors));

				$.each(errors, function(i, v) {
					$(".editProfileStatus").html("<span class='error'>"+i+": "+v+"</span>").fadeIn();
				});

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
