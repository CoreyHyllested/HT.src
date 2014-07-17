function addPortfolioInformation(fd) {
	console.log('addPortfolioInformation() -- enter');

	fd.csrf_token = $('.lessonFormButtonContainer #csrf_token').val();
	fd.lesson_id = $('#lessonForm').attr("data-lesson-id");

	$(".editPortfolioListItem").each(function(i, el) {
		var img	= new Object();
		img.idx	= $(el).index();
		img.old	= $(el).attr('order');
		img.cap	= $(this).find(".editPortfolioImage").data("title");
		var img_id	= $(this).find(".editPortfolioImage").data("id");
		console.log("img id is"+img_id);
		fd[img_id] = JSON.stringify(img);
		console.log('fd['+img_id+'] is '+fd[img_id]);
	});
	return fd;
}



function savePortfolio() {
	var fd = {};
	fd.csrf_token = $('.lessonFormButtonContainer #csrf_token').val();
	fd.lesson_id = $('#lessonForm').attr("data-lesson-id");
	
	console.log("-----------------------");
	console.log("savePortfolio : csrf_token: "+fd.csrf_token);
	console.log("savePortfolio : lesson_id: "+fd.lesson_id);

	// var images = [];

	//TODO replace with addPortfolioInformation
	$(".editPortfolioListItem").each(function(i, el) {
		var img	= new Object();
		img.idx	= $(el).index();
		img.old	= $(el).attr('order');
		img.cap	= $(this).find(".editPortfolioImage").data("title");
		var img_id	= $(this).find(".editPortfolioImage").data("id");
		console.log("img id is"+img_id);
		fd[img_id] = JSON.stringify(img);
		console.log('fd['+img_id+'] is '+fd[img_id]);
	});

	// console.log("savePortfolio : Images: "+JSON.stringify(images));

	console.log("savePortfolio : FD: "+JSON.stringify(fd));

	$.ajax({ url : "/portfolio/update/",
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
					var lessonID = $('#lessonForm').attr("data-lesson-id");
					$.when(getLessonData(lessonID)).then(getLessonImages(lessonID));
					$(".lessonEditPhotosStatus").empty();
					$(".lessonNavItem[data-target-page=" + lessonID + "]").addClass("active");
					history.pushState({title: "review"}, "", '/lesson/create#review');
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

$(document).ready(function(){

	$(".editPortfolioWrapper .editPortfolioList").sortable({
	    items:'.editPortfolioListItem',
	    cursor: 'move',
	    opacity: 0.5,
	    containment: '.editPortfolioWrapper',
	    tolerance: 'intersect',
	    /*start: function(event, ui){console.log(ui.item.index());},
	    update: function(event, ui) {} */
	});

	$(".lessonEditPhotosContainer .editPortfolioList").sortable({
	    items:'.editPortfolioListItem',
	    cursor: 'move',
	    opacity: 0.5,
	    containment: '.lessonEditPhotosContainer',
	    tolerance: 'intersect',
	    /*start: function(event, ui){console.log(ui.item.index());},
	    update: function(event, ui) {} */
	});


	$(".img-delete").click(function() {
		var img_id = $(this).parent().siblings(".editPortfolioImage").data("id");
		$(this).parent().parent().parent().parent().remove();
		$("#editPortfolioDoneContinueButton").hide();
		$("#editPortfolioDoneButton").show();
		//console.log("deleted: " + img_id);
	});

	$(".editPortfolioSave").click(function() {
		var caption = $(this).parent().siblings(".caption").children(".editPortfolioImageCaption").val();
		$(this).parent().siblings(".editPortfolioImage").data("title", caption);
		$(this).parent().fadeOut();
	});

	$(".editPortfolioImageCaption").keyup(function(){
		$("#editPortfolioDoneContinueButton").hide();
		$("#editPortfolioDoneButton").show();
		$(this).parent().siblings(".save-button").fadeIn();
	});

	$("#editPortfolioDoneButton").off().on('click', function(e) {
		e.preventDefault();
		savePortfolio();
	});
});
