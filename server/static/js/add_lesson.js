
$(document).ready(function() {
	var firstPage = "overview";
	var lastPage = "review";
	var lessonID = $("#addLessonForm").attr("data-lesson-id");

	// Form Navigation and State Management

	$(document.body).on("click", "#topLeftNavBack", function(e) {
		e.preventDefault();
		window.history.back();	
	});

	if (window.location.hash) {
		$(".addLessonNavItem").removeClass("active");
		var hash = window.location.hash.substring(1);	
		if (hash == "edit_photos") {
			editPortfolioImages(lessonID);
		} else if (hash == "review") {
			$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
		}
		$('#'+hash).show();	
		$(".addLessonNavItem[data-target-page=" + hash + "]").addClass("active");		
		history.replaceState({title: hash}, "", '');
	} else {
		// Default to first page
		$('#'+firstPage).show();
		$(".addLessonNavItem[data-target-page=" + firstPage + "]").addClass("active");
		history.replaceState({title: firstPage}, "", '');
	}

	window.onpopstate = function(event) {
		if (event.state) {
			var page_title = event.state.title;
			$('.addLessonFormPage').hide();
			$(".addLessonNavItem").removeClass("active");
			if (page_title == "edit_photos") {
				editPortfolioImages(lessonID);
			} else if (page_title == "review") {
				$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
			}
			
			$("#"+page_title).show();
			$(".addLessonNavItem[data-target-page=" + page_title + "]").addClass("active");
		}
	};	

	$('.addLessonNavItem').click(function() {
		$('.addLessonFormPage').hide();
		$(".addLessonNavItem").removeClass("active");
		var target = $(this).attr("data-target-page");
		if (target == "edit_photos") {
			editPortfolioImages(lessonID);
		} else if (target == "review") {
			$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
		}
		$("#"+target).show();
		$(this).addClass("active");
		history.pushState({title: target}, "", '/lesson/create/'+lessonID+'#'+target);
	});

	$(document.body).on("click", ".addLessonFormButton", function(e) {
		e.preventDefault();
		$('.addLessonFormPage').hide();
		$(".addLessonNavItem").removeClass("active");
		var currentPage = $(this).attr("data-current-page");
		var nextPage = $(".addLessonNavItem[data-target-page=" + currentPage + "]").next(".addLessonNavItem").attr("data-target-page");

		if (nextPage == "edit_photos") {
			editPortfolioImages(lessonID);
		} else if (nextPage == "review") {
			$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
		}

		$('#'+nextPage).show();
		$(".addLessonNavItem[data-target-page=" + nextPage + "]").addClass("active");
		history.pushState({title: nextPage}, "", '/lesson/create/'+lessonID+'#'+nextPage);
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
		$(".addLessonNavItem").removeClass("active");
		var currentPage = $(this).closest(".addLessonFormPage").attr("id");
		var prevPage = $(".addLessonNavItem[data-target-page=" + currentPage + "]").prev(".addLessonNavItem").attr("data-target-page");
		$('#'+prevPage).show();
		$(".addLessonNavItem[data-target-page=" + prevPage + "]").addClass("active");
		history.pushState({title: prevPage}, "", '/lesson/create/'+lessonID+'#'+prevPage);
	})

	// Form element Behavior

	$("#addressFields").css("opacity", .4).attr("disabled", "disabled");

	if ($('#addLessonPlace-2').is(":checked")) {
		$("#addressFields").css("opacity", 1).removeAttr("disabled");
	}


	$('input[name="addLessonPlace"]').click(function() {
		if ($(this).val() == "addLessonPlaceTeacher") {
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
	$(".addLessonReviewIndustry").text($("#addLessonIndustry option:selected").text());
	$(".addLessonReviewSchedule").text($("#addLessonAvail").val());
	$(".addLessonReviewDuration").text($("#addLessonDuration option:selected").text());
	$(".addLessonReviewRate").text($("#addLessonRate").val());
	if ($("#addLessonRateUnit").val() == "perHour") {
		$(".addLessonReviewRate").append(" per hour")
	} else {
		$(".addLessonReviewRate").append(" per lesson")
	}
	

	var placeOptID = $("input[name='addLessonPlace']:checked").attr("id");
	var placeOptText = $("label[for='"+placeOptID+"']").html();

	console.log("getLessonData: placeOptID: "+placeOptID);
	console.log("getLessonData: placeOptText: "+placeOptText);

	$(".addLessonReviewPlace").text(placeOptText);

	var availOptID = $("input[name='addLessonAvail']:checked").attr("id");
	var availOptText = $("label[for='"+availOptID+"']").html();

	$(".addLessonReviewAvail").text(availOptText);

	if (placeOptID == "addLessonPlace-2") {
		console.log("getLessonData: Assembling teacher address");
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
	}

}


function getLessonImages(lesson_id) {
	// $(".addLessonReviewPortfolio").empty();
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
