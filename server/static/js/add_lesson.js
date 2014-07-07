
$(document).ready(function(){

	var firstPage = "overview";
	var lastPage = "review";
	var lessonID = $("#addLessonForm").attr("data-lesson-id");

	// Form Navigation and State Management

	$(document.body).on("click", "#topLeftNavBack", function(e) {
		e.preventDefault();
		window.history.back();	
	});

	if (window.location.hash) {
		var hash = window.location.hash.substring(1);	
		if (hash == "edit_photos") {
			editPortfolioImages(lessonID);
		} else if (hash == "review") {
			$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
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
				editPortfolioImages(lessonID);
			} else if (page_title == "review") {
				$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
			}
			
			$("#"+page_title).show();
		}
	};	

	$('.addLessonNavLink').click(function() {
		$('.addLessonFormPage').hide();
		var target = $(this).attr("data-target-page");
		// $('.addLessonHeaderPageName').text($("#"+target+' .formTitle').text());
		if (target == "edit_photos") {
			editPortfolioImages(lessonID);
		} else if (target == "review") {
			$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
		}
		$("#"+target).show();
		history.pushState({title: target}, "", '/lesson/create#'+target);
	});

	$(document.body).on("click", ".addLessonFormButton", function(e) {
		e.preventDefault();
		$('.addLessonFormPage').hide();
		var currentPage = $(this).attr("data-current-page");
		var nextPage = $(".addLessonNavLink[data-target-page=" + currentPage + "]").parent().next(".addLessonNavItem").children().attr("data-target-page");

		if (nextPage == "edit_photos") {
			editPortfolioImages(lessonID);
		} else if (nextPage == "review") {
			$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
		}

		// $('.addLessonHeaderPageName').text($('#'+nextPage+' .formTitle').text());
		$('#'+nextPage).show();

		history.pushState({title: nextPage}, "", '/lesson/create#'+nextPage);
	});


	$('.addLessonFormButtonSubmit').click(function(e) {
		e.preventDefault();

		console.log("---------");
		console.log("Lesson Form was submitted");

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


function editPortfolioImages(lesson_id) {

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
				$("#editPortfolioDoneContinueButton").hide();
				$("#editPortfolioDoneButton").show();					
				// $('#sendMessage').bind('click', savePortfolio);
			},
			error : function(response) {
				console.log("AJAX error");
			}
	});

	return false;

}

function getLessonData(lesson_id) {

	console.log("---------------");
	console.log("getLessonData: Populating lesson data - lesson id: "+lesson_id);

	// $(".addLessonReviewData, .addLessonReviewDataDetails").empty();

	$(".addLessonReviewTitle").text($("#addLessonTitle").val());
	$(".addLessonReviewDescription").text($("#addLessonDescription").val());
	$(".addLessonReviewIndustry").text($("#addLessonIndustry").val());
	$(".addLessonReviewSchedule").text($("#addLessonAvail").val());
	$(".addLessonReviewDuration").text($("#addLessonDuration").val());
	$(".addLessonReviewRate").text($("#addLessonRate").val() + " " + $("#addLessonRateUnit").val());

	var placeOptVal = $("input[name='addLessonPlace']:checked").val();

	console.log("getLessonData: placeOptVal: "+placeOptVal);

	switch (placeOptVal) {
		case "0":
			$(".addLessonReviewLocation").text("Flexible - I will arrange with student");
			break;		
		case "1":
			$(".addLessonReviewLocation").text("Student's Place");
			break;		
		case "2":
			console.log("getLessonData: OK, assembling address");
			$(".addLessonReviewLocation").text("My Place:");
			var address1 = $("#addLessonAddress1").val();
			var address2 = $("#addLessonAddress2").val();
			var city = $("#addLessonCity").val();
			var state = $("#addLessonState").val();
			var zip = $("#addLessonZip").val();
			var details = $("#addLessonAddressDetails").val();

			var addressString = address1+"<br>";
			if (address2 != ""){
				addressString += address2+"<br>";
			}
			addressString += city+", "+state+"  "+zip+"<br>";
			if (details != ""){
				addressString += details+"<br>";
			}

			console.log("getLessonData: AddressString: "+addressString);
			$(".addLessonReviewAddress").html(addressString);
			break;
	}

}


function getLessonImages(lesson_id) {
	// $(".addLessonReviewPortfolio").empty();
	var fd = {};
	fd.lesson_id = lesson_id;

	$.ajax({ url : "/get_lesson_images",
			type : "GET",
			data : fd,
			success : function(response) {
				console.log("getLessonImages - AJAX success");
				console.log("getLessonImages - Response: "+JSON.stringify(response));
				$(".addLessonReviewPortfolio").empty();
				$.each(response.images, function() {
					console.log("IMAGE: "+this.img_id);
					$(".addLessonReviewPortfolio").append("<div class='portfolioImageWrapper'><img src='https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/"+this.img_id+"' class='portfolioImage'><div class='portfolioImageCaption'>"+this.img_comment+"</div></div>");
				});
		
			},
			error : function(response) {
				console.log("AJAX error");
			}
	});

	return false;
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
