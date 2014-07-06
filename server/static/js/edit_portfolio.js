function savePortfolio() {
	var fd = {};
	fd.csrf_token = $('.addLessonFormButtonContainer #csrf_token').val();
	fd.lesson_id = $('#addLessonForm').attr("data-lesson-id");
	
	console.log("-----------------------");
	console.log("savePortfolio : csrf_token: "+fd.csrf_token);
	console.log("savePortfolio : lesson_id: "+fd.lesson_id);

	// var images = [];

	$(".editPortfolioListItem").each(function(i, el) {
		var img	= new Object();
		img.idx	= $(el).index();
		img.old	= $(el).attr('order');
		img.cap	= $(this).find(".editPortfolioImage").data("title");
		var img_id	= $(this).find(".editPortfolioImage").data("id");
		console.log("img id is"+img_id);
		fd[img_id] = JSON.stringify(img);
		console.log("fd[img_id] is "+fd[img_id]);
	});

	// fd.images = JSON.stringify(images);

	

	

	// console.log("savePortfolio : Images: "+JSON.stringify(images));

	console.log("savePortfolio : FD: "+JSON.stringify(fd));

	// fd.append('images', images.length);

	$.ajax({ url : "/portfolio/update/",
			type : "POST",
			data : fd,
			dataType: 'json',
			success : function(response) {
				console.log("AJAX success");
				$(".addLessonEditPhotosStatus").html("<span class='success'>Images successfully updated!</span>");
			},
			error : function(response) {
				console.log("AJAX error");
				$(".addLessonEditPhotosStatus").html("<span class='error'>Whoops! Error updating images.</span>");
			}
	});




	// var xhr = new XMLHttpRequest();
	// xhr.onreadystatechange = function(e) {
	// 	if (4 == this.readyState) {
	// 		console.log(['xhr post complete ', e]);
	// 		if (this.status == 200) {
	// 			msg = JSON.parse(xhr.responseText);
	// 			console.log(xhr.responseText);
	// 			openAlertWindow(msg['usrmsg']);
	// 		} else if (this.status == 500) {
	// 			msg = JSON.parse(xhr.responseText);
	// 			console.log(['xhr upload complete', e]);
	// 			openAlertWindow('Failure: ' + msg['usrmsg']);
	// 		} else {
	// 			msg = JSON.parse(xhr.responseText);
	// 			openAlertWindow(msg['usrmsg']);
	// 		}
	// 	}
	// };

	// xhr.open('POST', "/portfolio/update/", true);
	// xhr.send(fd);


	return false;
}

$(document).ready(function(){

	$(".editPortfolioWrapper .editPortfolioList").sortable({
	    items:'.editPortfolioListItem',
	    cursor: 'move',
	    opacity: 0.5,
	    containment: '.editPortfolioWrapper',
	    tolerance: 'pointer',
	    /*start: function(event, ui){console.log(ui.item.index());},
	    update: function(event, ui) {} */
	});

	$(".addLessonEditPhotosContainer .editPortfolioList").sortable({
	    items:'.editPortfolioListItem',
	    cursor: 'move',
	    opacity: 0.5,
	    containment: '.addLessonEditPhotosContainer',
	    tolerance: 'pointer',
	    /*start: function(event, ui){console.log(ui.item.index());},
	    update: function(event, ui) {} */
	});


	$(".img-delete").click(function() {
		var img_id = $(this).parent().siblings(".editPortfolioImage").data("id");
		$(this).parent().parent().parent().parent().remove();
		//console.log("deleted: " + img_id);
	});

	$(".editPortfolioSave").click(function() {
		var caption = $(this).parent().siblings(".caption").children(".editPortfolioImageCaption").val();
		$(this).parent().siblings(".editPortfolioImage").data("title", caption);
		$(this).parent().fadeOut();
	});

	$(".editPortfolioImageCaption").keyup(function(){
		$(this).parent().siblings(".save-button").fadeIn();
	});

	$("#editPortfolioDoneButton").off().on('click', function(e) {
		e.preventDefault();
		savePortfolio();
		$(".addLessonFormButtonContainer").children(".addLessonFormButton").toggleClass("addLessonFormButton addLessonFormButton").text("Continue");
	});
});
