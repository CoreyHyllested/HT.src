
$(document).ready(function() {
	var firstPage = "overview";
	var lastPage = "review";
	var lessonID = $("#lessonForm").attr("data-lesson-id");
	var referrer = document.referrer;
	console.log("referrer is "+referrer);

	// Form Navigation and State Management

	$(document.body).on("click", "#topLeftNavBack", function(e) {
		e.preventDefault();
		// window.history.back();	
		document.location.href = referrer;
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
		history.pushState({title: target}, "", '/lesson/new/'+lessonID+'#'+target);
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
		history.pushState({title: nextPage}, "", '/lesson/new/'+lessonID+'#'+nextPage);
	});

	$('#lessonSave').click(function(e) {
		e.preventDefault();
		console.log("---------");
		console.log("Save was clicked");

		saveLessonForm(lessonID); 	
	});

	$('.lessonFormButtonSubmit').click(function(e) {
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
		history.pushState({title: prevPage}, "", '/lesson/new/'+lessonID+'#'+prevPage);
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
				$(".lessonEditPhotosContainer").html(page_content);
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

	$.ajax({ url : "/get_lesson_images",
			type : "GET",
			data : fd,
			success : function(response) {
				console.log("getLessonImages - AJAX success");
				console.log("getLessonImages - Response: "+JSON.stringify(response));
				$(".lessonReviewPortfolio").empty();
				$.each(response.images, function() {
					console.log("IMAGE: "+this.img_id);
					$(".lessonReviewPortfolio").append("<div class='portfolioImageWrapper'><img src='https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/"+this.img_id+"' class='portfolioImage'><div class='portfolioImageCaption'>"+this.img_comment+"</div></div>");
				});
		
			},
			error : function(response) {
				console.log("AJAX error");
			}
	});

	return false;
}


function saveLessonForm(lesson_id) {

	var fd = new FormData($('#lessonForm')[0]);
	fd.append('saved', "true")
	// fd.append('csrf_token', $('#csrf_token').val())
	// fd.append('lesson_title', $('#lessonTitle').val())
	// fd.append('lesson_description', $('#lessonDescription').val())
	// fd.append('lesson_address_1', $('#lessonAddress1').val())
	// fd.append('lesson_address_2', $('#lessonAddress2').val())
	// fd.append('lesson_city', $('#lessonCity').val())
	// fd.append('lesson_state', $('#lessonState').val())
	// fd.append('lesson_zip', $('#lessonZip').val())
	// fd.append('lesson_country', $('#lessonCountry').val())
	// fd.append('lesson_address_details', $('#lessonAddressDetails').val())
	// fd.append('lesson_rate', $('#lessonRate').val())
	// fd.append('lesson_rate_unit', $('#lessonRateUnit').val())
	// fd.append('lesson_loc_option', $('#lessonPlace').val())
	// fd.append('lesson_industry', $('#lessonIndustry').val())
	// fd.append('lesson_duration', $('#lessonDuration').val())
	// fd.append('lesson_avail', $('#lessonAvail').val())
	// Note - We don't need to set flags here. That's handled by ht_update_lesson.

	console.log("saveLessonForm - version is "+fd["version"]);

	$.ajax({ url	: "/lesson/update/"+lesson_id,
			type	: "POST",
			data : fd,
			processData: false,
  			contentType: false,
			success : function(data) {
			 	console.log("AJAX Success - lesson saved.");
			 	$("#lessonSave").html("Saved").css("color","gray");

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
