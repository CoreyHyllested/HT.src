function savePortfolio() {
	var fd = new FormData();
	var csrf = "{{ csrf_token() }}";
	fd.append('csrf_token', csrf);
	var images = [];

	$(".editPortfolioList li").each(function(i, el) {
		var img	= new Object();
		img.idx	= $(el).index();
		img.old	= $(el).attr('order');
		img.cap	= $(this).find(".editPortfolioImage").data("title");
		img_id	= $(this).find(".editPortfolioImage").data("id");
		images.push(img);
		fd.append(img_id, JSON.stringify(img));
	});
	fd.append('images', images.length);
	console.log(JSON.stringify(images));

	var xhr = new XMLHttpRequest();
	xhr.onreadystatechange = function(e) {
		if (4 == this.readyState) {
			console.log(['xhr post complete ', e]);
			if (this.status == 200) {
				msg = JSON.parse(xhr.responseText);
				console.log(xhr.responseText);
				openAlertWindow(msg['usrmsg']);
			} else if (this.status == 500) {
				msg = JSON.parse(xhr.responseText);
				console.log(['xhr upload complete', e]);
				openAlertWindow('Failure: ' + msg['usrmsg']);
			} else {
				msg = JSON.parse(xhr.responseText);
				openAlertWindow(msg['usrmsg']);
			}
		}
	};
	xhr.open('POST', "/portfolio/update/", true);
	xhr.send(fd);
	return false;
}

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

$(".editPortfolioDoneButton").click(function() {
	savePortfolio();
})
