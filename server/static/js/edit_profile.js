$(document).ready(function() {

	// Form Navigation and State Management

	var firstPage = "general";
	var lastPage = "status";
	var path = "/profile/edit";
	var formMode = "basic"; // basic or mentor - required to know how to validate

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
		if (currentNav.hasClass("disabled")) {
			activateMentorForm();
		}
		history.replaceState({title: hash}, "", '');

	} else {
		// Default to first page
		$('#'+firstPage).show();
		var currentNav = $(".editProfNavItem[data-target-page=" + firstPage + "]");
		history.replaceState({title: firstPage}, "", '');
	}
	currentNav.addClass("active");
	$('.editProfHeaderPageName').text(currentNav.text());

	// evaluate flags/user state - gray out mentor nav if not activated.

	// $(".mentorFormNavItem").addClass("disabled");

	var flags = $(".editProfFlags").data("flags");

	if (flags > 0){
		activateMentorForm();
	} else {
		$("#editProfNavItemMentor").show();
	}	


	window.onpopstate = function(event) {
		if (event.state) {
			var page_title = event.state.title;
			$('.editProfFormPage').hide();
			$("#"+page_title).show();
		}
	};	

	// Navigation

	$(document).on("click", '.editProfNavItem:not(.disabled)', function() {
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
		nextNav.addClass("active");
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
		prevNav.addClass("active");
		history.pushState({title: prevPage}, "", path+'#'+prevPage);
	})

	$(".editProfActivate").click(function(e) {
		e.preventDefault();
		$('.editProfFormPage').hide();
		$(".editProfNavItem").removeClass("active");
		activateMentorForm();
		
		var nextPage = "guidelines";
		var nextNav = $(".editProfNavItem[data-target-page=" + nextPage + "]");
		$('#'+nextPage).show();
		$('.editProfHeaderPageName').text(nextNav.text());
		nextNav.addClass("active");
		history.pushState({title: nextPage}, "", path+'#'+nextPage);		

	})	

	$(".editProfSave").click(function(e) {
		e.preventDefault();

		var formPage = $(this).data("currentPage");
		console.log("formPage: "+formPage);

		saveProfile(formPage);
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

	$("#edit_rate").blur(function() {
		
		var rate = $(this).val();

		console.log("type of rate: "+typeof rate);

		if (isNaN(rate)) { // string
			console.log("Ok it's not a number");
			$(this).val(0);
			$(this).next(".formFieldCaption").text("Please only enter a number here.").fadeIn();

		} else {

			if (rate % 1 === 0) { // integer
				$(this).next(".formFieldCaption").fadeOut().empty();
			} else { // float
				var rounded = Math.round(rate);
				$(this).val(rounded);
				$(this).next(".formFieldCaption").text("Please keep it to a whole dollar amount (or zero).").fadeIn();
			}
		}
		setTimeout(function() {
			$('.formFieldCaption').fadeOut(400);
		}, 3000 );
		
	})

	if ($("#edit_oauth_stripe").val() != "") {
		$("#edit_oauth_stripe").next(".formFieldCaption").text("Account number imported.").fadeIn();
	}

});

function activateMentorForm() {
	formMode = "mentor";
	$(".mentorNav").css("opacity", 1);
	$(".mentorFormNavItem").removeClass("disabled");
}

function saveProfile(formPage) {

	var fd = new FormData($('#editProfForm')[0]);

	console.log("saving from formPage: "+formPage);
	
	formMode = "page";
	if (formPage == "submit") {
		formPage = "full";
		formMode = "full";
	}

	fd.append('formPage', formPage);
	fd.append('formMode', formMode);

	// Remove error indicators
	$(".formFieldError").slideUp().html("");
	$(".formField").css("border-color", "#e1e8ed");
	$(".editProfNavItem").each(function() {
		var navDefaultIcon = $(this).attr("data-default-icon");
		$(this).css("color", "rgba(0, 0, 0, 0.7)").children("i.icon").attr("class", "fa fa-fw "+navDefaultIcon);		
	});


	$(".editProfFormStatus").html("Saving...").fadeIn();

	$.ajax({ url	: "/profile/update",
			type	: "POST",
			data : fd,
			processData: false,
  			contentType: false,
			success : function(response) {

			 	console.log("AJAX Success - profile saved.");		 	

			 	console.log("formPage:" + formPage);

			 	// Add progress marks
			 	// if (formPage != "full"){
			 	// 	var navItem = ".editProfNavItem[data-target-page='" + formPage + "']";
			 	// 	console.log("navItem: "+navItem);
			 	// 	$(".editProfNavItem[data-target-page='" + formPage + "']").children("i.progress").show();
			 	// }
			 	
			 	// Remove the image from the file element
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

				showErrors(errors);

			}
	});
	return false;

}


function showErrors(errors) {

	$(".editProfFormStatus").empty();

	// iterate thru errors, create status messages, highlight form and navigation elements.
	$.each(errors, function(e, error){
		// "e" here would be the form element name that has the error, e.g. "prof_name"
		var element = "#"+e;
		var page = $(element).parents(".editProfFormPage").attr("id");
		var navItem = ".editProfNavItem[data-target-page='" + page + "']";

		console.log("showErrors: element: "+element);
		console.log("showErrors: page: "+page);
		console.log("showErrors: navItem: "+navItem);

		$(element).css("border-color", "red");
		$(element).prevAll(".formFieldError").html(error).slideDown();


		$("#"+page).find(".editProfFormStatus").html("<span class='error'>There was a problem - please check the form.</span>").fadeIn();

		$(navItem).css("color", "red");
		$(navItem).children("i.progress").hide();

	});

	$("#submit").find(".editProfFormStatus").html("<span class='error'>There was a problem - please check the form.</span>").fadeIn();

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
