
$(document).ready(function() {
	var firstPage = "overview";
	var lastPage = "review";
	var lessonID = $("#lessonForm").attr("data-lesson-id");
	

	// version will be "edit" if user is editing existing, or "first" if it's a first-time lesson creation. It is "new" for general "add lesson" state
	var version = $("#version").val(); 

	// statePath determines the uri pushed by the state functions - depends on the version (do we make the uri "/edit" or "/new")
	var statePath = "/lesson/new/";
	if (version == "edit") {
		statePath = "/lesson/edit/";
	}

	var lesson_flags = $(".lessonHeaderPageStatus").attr("data-flags");
	
	// evaluate lesson flags/state and generate the text on the form
	generateStatus(lessonID, lesson_flags);
	// check for error messages in the form and indicate them in the navigation
	showErrors();

	console.log("version is "+version);
	var referrer = document.referrer;
	console.log("referrer is "+referrer);

	// Form Navigation and State Management

	$(document.body).on("click", "#topLeftNavBack", function(e) {
		e.preventDefault();
		// window.history.back();	
		// document.location.href = referrer;
		document.location.href = "/dashboard";
	});

	if (window.location.hash) {
		$(".lessonNavItem").removeClass("active");
		var hash = window.location.hash.substring(1);	
		if (hash == "edit_photos") {
			editPortfolioImages(lessonID);
		} else if (hash == "review") {
			$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
		}
		$('#'+hash).show();	
		$(".lessonNavItem[data-target-page=" + hash + "]").addClass("active");		
		history.replaceState({title: hash}, "", '');
	} else {
		// Default to first page
		$('#'+firstPage).show();
		$(".lessonNavItem[data-target-page=" + firstPage + "]").addClass("active");
		history.replaceState({title: firstPage}, "", '');
	}

	window.onpopstate = function(event) {
		if (event.state) {
			var page_title = event.state.title;
			$('.lessonFormPage').hide();
			$(".lessonNavItem").removeClass("active");
			if (page_title == "edit_photos") {
				editPortfolioImages(lessonID);
			} else if (page_title == "review") {
				$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
			}
			
			$("#"+page_title).show();
			$(".lessonNavItem[data-target-page=" + page_title + "]").addClass("active");
		}
	};	

	$('.lessonNavItem').click(function() {
		$('.lessonFormPage').hide();
		$(".lessonNavItem").removeClass("active");
		var target = $(this).attr("data-target-page");
		if (target == "edit_photos") {
			editPortfolioImages(lessonID);
		} else if (target == "review") {
			$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
		}
		$("#"+target).show();
		$(this).addClass("active");
		history.pushState({title: target}, "", statePath+lessonID+'#'+target);
	});

	$(document.body).on("click", ".lessonFormButton", function(e) {
		e.preventDefault();
		$('.lessonFormPage').hide();
		$(".lessonNavItem").removeClass("active");
		var currentPage = $(this).attr("data-current-page");
		var nextPage = $(".lessonNavItem[data-target-page=" + currentPage + "]").next(".lessonNavItem").attr("data-target-page");

		if (nextPage == "edit_photos") {
			editPortfolioImages(lessonID);
		} else if (nextPage == "review") {
			$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
		}

		$('#'+nextPage).show();
		$(".lessonNavItem[data-target-page=" + nextPage + "]").addClass("active");
		history.pushState({title: nextPage}, "", statePath+lessonID+'#'+nextPage);
	});

	$(document.body).on("click", "#lessonSave", function(e) {
		e.preventDefault();
		console.log("---------");
		console.log("Save was clicked");

		saveLessonForm(lessonID); 	
	});

	$(document.body).on("click", ".lessonFormButtonSave", function(e) {
		e.preventDefault();
		console.log("---------");
		console.log("Save was clicked");

		saveLessonForm(lessonID); 	
	});

	$(document.body).on("click", ".lessonFormButtonSubmit", function(e) {
		e.preventDefault();

		console.log("---------");
		console.log("Lesson Form was submitted");

		$("#lessonForm").submit();
	});

	$('.lessonFormPrevious').click(function(e) {
		e.preventDefault();
		$('.lessonFormPage').hide();	
		$(".lessonNavItem").removeClass("active");
		var currentPage = $(this).closest(".lessonFormPage").attr("id");
		var prevPage = $(".lessonNavItem[data-target-page=" + currentPage + "]").prev(".lessonNavItem").attr("data-target-page");
		$('#'+prevPage).show();
		$(".lessonNavItem[data-target-page=" + prevPage + "]").addClass("active");
		history.pushState({title: prevPage}, "", statePath+lessonID+'#'+prevPage);
	})

	// Form element Behavior

	$("#addressFields").css("opacity", .4).attr("disabled", "disabled");

	if ($('#lessonPlace-2').is(":checked")) {
		$("#addressFields").css("opacity", 1).removeAttr("disabled");
	}


	$('input[name="lessonPlace"]').click(function() {
		if ($(this).val() == "2") {
		  $("#addressFields").css("opacity", 1).removeAttr("disabled");
		} else {
		  $("#addressFields").css("opacity", .4).attr("disabled", "disabled");
		} 
	});

	$("#lessonDuration").change(function() {
		var choiceText = $(this).find(":selected").text();
		$(".rateUnitCaption").text("Lesson Duration: "+choiceText);
	});


	$('#lessonForm :input').change(function() {
		$("#lessonSave").html("Save").css("color","#1488CC");
	});
	

	$('#updateLessonPortfolioButton').click(function(e) {
		e.preventDefault();
		saveLessonPortfolio();
	});


	// The "make lesson live" checkbox must use a proxy, because the visible checkbox is outside of the form (bc of the embedded image forms.)
	// So when the visible 'proxy' element is checked or unchecked, the same happens to the real, hidden one, which is submitted thru wtforms.
	var checkState = $('#lessonMakeLive').prop('checked');
	$('#lessonMakeLiveProxy').prop('checked', checkState);

	$('#lessonMakeLiveProxy').click(function() {
		var newCheckState = $('#lessonMakeLiveProxy').prop('checked');
		$('#lessonMakeLive').prop('checked', newCheckState);

		// $('#lessonFormButtonFinal').toggleClass("lessonFormButtonSubmit lessonFormButtonSave").toggleClass("blueButton whiteButton");
		
		console.log("Check state changed - value: "+ newCheckState);

		// if (newCheckState == true) {
		// 	$('#lessonFormButtonFinal').text("Submit Lesson").css("color","#fff");
		// } else {
		// 	$('#lessonFormButtonFinal').text("Save for Later").css("color","#1488CC");
		// }

	});



});

function showErrors() {

	// If a page has an error in it, mark it in the navigation tab.

	$(".lessonNavItem").each(function() {

		var defaultIcon = $(this).attr("data-default-icon");
		
		$(this).css("color", "rgba(0, 0, 0, 0.7)").children("i").attr("class", "fa fa-fw "+defaultIcon);

		var target = $(this).attr("data-target-page");
		var error_status = $("#"+target).find(".formFieldErrors").length;
		if (error_status) {
			$(this).css("color", "red").children("i").attr("class", "fa fa-fw fa-exclamation");
		}

	});

}

function generateStatus(lesson_id, lesson_flags) {

	var statusText = "Lesson Status: ";

	switch (parseInt(lesson_flags)) {
		case 0:
			statusText += "Incomplete";
			break;
		case 1:
			statusText += "Saved but not submitted";
			break;		
		case 2:
			statusText += "Submitted and awaiting approval";
			break;		
		case 3:
			statusText += "Approved and public";
			break;
		default:
			statusText += "Unknown";
			break;
	}

	$(".lessonHeaderPageStatus").text(statusText);
	if (parseInt(lesson_flags) > 1){
		$(".lessonHeaderPageStatus").append("&nbsp;&nbsp;<a href='/lesson/"+lesson_id+"'>(View lesson page)</a>");
	}
}


function saveLessonPortfolio() {
	/* forked from edit_portfolio.js, savePortfolio */

	var fd = {};
	addPortfolioInformation(fd);

	var lessonID = $('#lessonForm').attr("data-lesson-id");
	$.ajax({ url : '/lesson/' + lessonID + '/image/update',
			type : "POST",
			data : fd,
			dataType: 'json',
			success : function(response) {
				console.log("AJAX success");
				$("#lessonSave").html("Save").css("color","#1488CC");
				$(".lessonEditPhotosStatus").html("<span class='success'>Images successfully updated! Continuing...</span>");

				setTimeout(function() {
					$('.lessonFormPage').hide();
					$(".lessonNavItem").removeClass("active");
					$('#review').show();

					$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
					$(".lessonEditPhotosStatus").empty();
					$(".lessonNavItem[data-target-page=" + lessonID + "]").addClass("active");
					history.pushState({title: "review"}, "", statePath='#review');
				}, 2000);

				// Uncomment this and comment the setTimeout function if we want user to manually continue.
				// $("#editPortfolioDoneContinueButton").show();
				// $("#editPortfolioDoneButton").hide();
			},
			error : function(response) {
				console.log("AJAX error");
				$(".lessonEditPhotosStatus").html("<span class='error'>Whoops! Error updating images.</span>");
				// $(".lessonFormButtonContainer").children(".editPortfolioDoneButton").toggleClass("editPortfolioDoneButton lessonFormButton").attr("id", "").on().text("Continue");
				$("#editPortfolioDoneContinueButton").show();
				$("#editPortfolioDoneButton").hide();
			}
	});

	return false;
}


function editPortfolioImages(lesson_id) {

	var fd = {};
	fd.lesson_id = lesson_id;
	$.ajax({ url : "/edit_portfolio",
			type : "GET",
			data : fd,
			success : function(response) {
				// console.log("AJAX success");
				var page_content = $(response).find('.editPortfolioListContainer').html();
				$(".lessonEditPhotosContainer").html(page_content);
				$.getScript("/static/js/edit_portfolio.js");
				$("#editPortfolioDoneContinueButton").hide();
				$("#updateLessonPortfolioButton").show();
				// $('#sendMessage').bind('click', savePortfolio);
			},
			error : function(response) {
				console.log("AJAX error");
				console.log(response);
			}
	});
	return false;
}


function getLessonData(lesson_id) {

	console.log("---------------");
	console.log("getLessonData: Populating lesson data - lesson id: "+lesson_id);

	$(".lessonReviewData, .lessonReviewDataDetails").empty();

	$(".lessonReviewTitle").text($("#lessonTitle").val());
	$(".lessonReviewDescription").text($("#lessonDescription").val());
	$(".lessonReviewIndustry").text($("#lessonIndustry option:selected").text());
	$(".lessonReviewSchedule").text($("#lessonAvail").val());
	$(".lessonReviewDuration").text($("#lessonDuration option:selected").text());
	$(".lessonReviewRate").text($("#lessonRate").val());
	if ($("#lessonRateUnit").val() == 0) {
		$(".lessonReviewRate").append(" per hour")
	} else {
		$(".lessonReviewRate").append(" per lesson")
	}
	

	var placeOptID = $("input[name='lessonPlace']:checked").attr("id");
	var placeOptText = $("label[for='"+placeOptID+"']").html();

	console.log("getLessonData: placeOptID: "+placeOptID);
	console.log("getLessonData: placeOptText: "+placeOptText);

	$(".lessonReviewPlace").text(placeOptText);

	var availOptID = $("input[name='lessonAvail']:checked").attr("id");
	var availOptText = $("label[for='"+availOptID+"']").html();

	$(".lessonReviewAvail").text(availOptText);

	if (placeOptID == "lessonPlace-2") {
		console.log("getLessonData: Assembling teacher address");
		var address1 = $("#lessonAddress1").val();
		var address2 = $("#lessonAddress2").val();
		var city = $("#lessonCity").val();
		var state = $("#lessonState").val();
		var zip = $("#lessonZip").val();
		var details = $("#lessonAddressDetails").val();

		var addressString = address1+"<br>";
		if (address2 != ""){
			addressString += address2+"<br>";
		}
		addressString += city+", "+state+"  "+zip+"<br>";
		if (details != ""){
			addressString += details+"<br>";
		}
		console.log("getLessonData: AddressString: "+addressString);
		$(".lessonReviewAddress").html(addressString);
	}

}


function getLessonImages(lesson_id) {
	// $(".lessonReviewPortfolio").empty();
	var fd = {};
	fd.lesson_id = lesson_id;
	if (!lesson_id) {
		console.log('getLessonImages: ERROR - lesson_id is null');
	}

	$.ajax({ url : '/lesson/'+lesson_id+'/images',
			type : "GET",
			data : fd,
			success : function(response) {
				console.log("getLessonImages - AJAX success");
				console.log("getLessonImages - Response: "+ JSON.stringify(response));
				$(".lessonReviewPortfolio").empty();
				$.each(response.portfolio, function() {
					console.log("IMAGE: "+this.img_id);

					$(".lessonReviewPortfolio").append("<div class='portfolioImageBox'><div class='portfolioImageWrapper'><img src='https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/"+this.img_id+"' class='portfolioImage'></div><div class='portfolioImageCaption'>"+this.img_comment+"</div></div>");

				});
		
			},
			error : function(response) {
				console.log("AJAX error");
				console.log(response);
			}
	});

	return false;
}


function saveLessonForm(lesson_id) {
	var fd = new FormData($('#lessonForm')[0]);
	fd.append('saved', "true")

	$.ajax({ url	: "/lesson/update/"+lesson_id,
			type	: "POST",
			data : fd,
			processData: false,
  			contentType: false,
			success : function(response) {
			 	console.log("AJAX Success - lesson saved.");
			 	$("#lessonSave").html("Saved").css("color","gray");
			 	$(".lessonFormButtonSave").html("Saved").css("color","gray");
			 	$(".formFieldErrors").remove();

			 	console.log("Flags: "+response.lesson_flags);

			 	generateStatus(response.lesson_flags);
			 	showErrors();

			 	// $(".lessonFormStatus").html("<span class='success'>Lesson saved.</span>").fadeIn();
				// setTimeout(function() {
				// 	$('.lessonFormStatus').fadeOut(1000);
				// }, 2000 );
			}, 
			error: function(response) {
				console.log("AJAX Error - lesson not saved.");
				// $(".lessonFormStatus").html("<span class='error'>Sorry, something went wrong. Lesson not saved.</span>").fadeIn();
			}
	});
	return false;
}
