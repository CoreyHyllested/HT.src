$(document).ready(function() {
	if (window.location.hash) {
		$(".editProfNavItem").removeClass("active");
		var hash = window.location.hash.substring(1);

		var currentNav = $(".editProfNavItem[data-target-page=" + hash + "]");
		$('#'+hash).show();
		history.replaceState({title: hash}, "", '');
	} else {
		// Default to first page
		$('#general').show();
		var currentNav = $(".editProfNavItem[data-target-page=general]");
		history.replaceState({title: "#general"}, "", '');
	}

	//set current #PAGE as active, using a class/decorator.
	currentNav.addClass("active");
	$('.editProfHeaderPageName').text(currentNav.text());

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
		history.pushState({title: target}, "", '/project/edit#'+target);
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
		history.pushState({title: nextPage}, "", '/project/edit#'+nextPage);
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
		history.pushState({title: prevPage}, "", '/project/edit#'+prevPage);
	})


	$(".editProfSave").click(function(e) {
		e.preventDefault();
		saveProject();
	});


	$(".timeSelector").css("opacity", .4).attr("disabled", "disabled");

	// When loading form - activate times when date is selected
	$(".daySelector").each(function() {
		if ($(this).prop("checked")) {
			$(this).siblings(".timeSelector").css("opacity", 1).removeAttr("disabled");
		}	
	});

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



function saveProject() {
	formPage = 'none';
	console.log("save project");
	var fd = new FormData($('#editProfForm')[0]);

	// reset all error indications.
	$(".formFieldError").slideUp().html("");
	$(".formField").css("border-color", "#e1e8ed");

	console.log("calling AJAX.");		 	
	$.ajax({ url	: "/project/update",
			type	: "POST",
			data : fd,
			processData: false,
  			contentType: false,
			success : function(response) {

			 	console.log("AJAX Success - project saved.");		 	

				if (formPage != "mentor") {
					$("#"+formPage+" .editProfFormStatus").html("<span class='success'>Changes Saved.</span>").fadeIn(400);
				}

				setTimeout(function() {
					$('.editProfFormStatus').fadeOut(400);
				}, 1600 );
			}, 

			error: function(xhr, status, error) {
				console.log("project not saved.");

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
	// iterate thru errors, highlight and navigation elements.

	$.each(errors, function(element, error) {
		var e = "#"+element;
		console.log("showErrors: " + element + ": " + error);
		$(e).prevAll(".formFieldError:first").html(error).fadeIn();
		$(e).css("border-color", "yellow");
	});

	$("#submit").find(".editProfFormStatus").html("<span class='error'>There was a problem - please check the form.</span>").fadeIn();
}

function createReader(input, whenReady) {
	var file = input.files[0];
	var imageType = /image.*/;

	if (input.files && file) {
		if (file.type.match(imageType)) {
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

}
