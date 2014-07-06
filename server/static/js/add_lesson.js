
$(document).ready(function(){

	var firstPage = "overview";
	var lastPage = "rate";
	// var lastPage = "edit_photos";
	var lessonID = $("#addLessonForm").attr("data-lesson-id");
	
	// Form Navigation and State Management

	$(document.body).on("click", "#topLeftNavBack", function(e) {
		e.preventDefault();
		window.history.back();	
	});

	if (window.location.hash) {
		var hash = window.location.hash.substring(1);	
		if (hash == "edit_photos") {
			loadPortfolioImages(lessonID);
		}	
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
			$('.addLessonFormPage').hide();
			if (page_title == "edit_photos") {
				loadPortfolioImages(lessonID);
			}			
			$("#"+page_title).show();
		}
	};	

	$('.addLessonNavLink').click(function() {
		$('.addLessonFormPage').hide();
		var target = $(this).attr("data-target-page");
		// $('.addLessonHeaderPageName').text($("#"+target+' .formTitle').text());
		if (target == "edit_photos") {
			loadPortfolioImages(lessonID);
		}
		$("#"+target).show();
		history.pushState({title: target}, "", '/lesson/create#'+target);
	});

	$(document.body).on("click", ".addLessonFormButton", function(e) {
		e.preventDefault();
		$('.addLessonFormPage').hide();
		var currentPage = $(this).attr("data-current-page");
		var nextPage = $('#'+currentPage).next('.addLessonFormPage').attr("id");
		

		if (nextPage == "edit_photos") {
			loadPortfolioImages(lessonID);
		}

		// $('.addLessonHeaderPageName').text($('#'+nextPage+' .formTitle').text());
		$('#'+nextPage).show();

		history.pushState({title: nextPage}, "", '/lesson/create#'+nextPage);
	});

	$('.addLessonFormButtonSubmit').click(function(e) {
		e.preventDefault();

		var formData = {};

		// formData.oauth_stripe = $("#oauth_stripe").val();
		// formData.ssAvailOption = $("#ssAvailOption").val();
		// formData.ssAvailTimes = $("#ssAvailTimes").val();
		// console.log(JSON.stringify(formData));		
		// console.log("Photo details: 'ssProfileImage' - "+ JSON.stringify($("#ssProfileImage")[0].files[0]));

		// Uncomment when ready to actually do the database stuff
		$("#addLessonForm").submit();
		

	});

	$('.addLessonFormPrevious').click(function(e) {
		e.preventDefault();
		$('.addLessonFormPage').hide();	

		var currentPage = $(this).closest(".addLessonFormPage").attr("id");
		var prevPage = $(".addLessonNavLink[data-target-page=" + currentPage + "]").parent().prev(".addLessonNavItem").children().attr("data-target-page");
		// $('.ssHeaderPageName').text($('#'+prevPage+' .formTitle').text());			
		$('#'+prevPage).show();
		history.pushState({title: prevPage}, "", '/lesson/create#'+prevPage);
	})

	// Form element Behavior

	$("#addressFields").css("opacity", .4).attr("disabled", "disabled");

	$('input[name="addLessonPlace"]').click(function() {
		if ($(this).val() == 2) {
		  $("#addressFields").css("opacity", 1).removeAttr("disabled");
		} else {
		  $("#addressFields").css("opacity", .4).attr("disabled", "disabled");
		} 
	});

	$("#addLessonDuration").change(function() {
		var choiceText = $(this).find(":selected").text();
		$(".rateUnitCaption").text("Lesson Duration: "+choiceText);
	});


});


function loadPortfolioImages(lesson_id) {

	var fd = {};
	fd.lesson_id = lesson_id;
	$.ajax({ url : "/edit_portfolio",
			type : "GET",
			data : fd,
			success : function(response) {
				// console.log("AJAX success");
				var page_content = $(response).find('.editPortfolioListContainer').html();
				$(".addLessonEditPhotosContainer").html(page_content);
				$.getScript("/static/js/edit_portfolio.js");
				// $('#sendMessage').bind('click', savePortfolio);
			},
			error : function(response) {
				console.log("AJAX error");
			}
	});

}

// Form Validation

function validateForm() {
	// Fetch form elements
	var name = document.forms["SignupNow"]["input_signup_name"];
	var email_address = document.forms["SignupNow"]["input_signup_email"];
	var password = document.forms["SignupNow"]["input_signup_password"];
	var confirm = document.forms["SignupNow"]["input_signup_confirm"];

	// Check for empty fields; if found, highlight them
	var form_fields = [name, email_address, password, confirm];
	for (var i = 0; i < form_fields.length; i++) {
		var current_element = form_fields[i];
		var current_value = form_fields[i].value;
		if (current_value.match(/^\s*$/)) {
			$(current_element).focus();
			return false;
		}
	}
}
