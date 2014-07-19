$(document).ready(function() {

	/* When visible 'Choose File...' is clicked, activate hidden 'Browse...' */
	$("#editChooseImage").click(function() {
   		$("#change-photo-button").click();
	});

	/* When the profile pic is clicked, activate hidden 'Browse...' */
	$("#profile_img").click(function() {
   		$("#change-photo-button").click();
	});


	$("#edit-save").click(function(e) {

		e.preventDefault();

		saveProfile();

	});

	

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



});


function saveProfile() {

	var fd = new FormData($('#editProfileForm')[0]);

	$.ajax({ url	: "/profile/update",
			type	: "POST",
			data : fd,
			processData: false,
  			contentType: false,
			success : function(response) {
			 	console.log("AJAX Success - profile saved.");

			 	openAlertWindow("Success: " + response.usrmsg);

			 	// $(".lessonFormStatus").html("<span class='success'>Lesson saved.</span>").fadeIn();
				// setTimeout(function() {
				// 	$('.lessonFormStatus').fadeOut(1000);
				// }, 2000 );
			}, 
			error: function(response) {
				console.log("AJAX Error - profile not saved.");
			
				openAlertWindow("Error: " + response.errors);
				// $(".lessonFormStatus").html("<span class='error'>Sorry, something went wrong. Lesson not saved.</span>").fadeIn();
			
			}
	});
	return false;

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
		    $('.ssUploadPreviewImage').attr('src', e.target.result).show();
		}
		reader.readAsDataURL(input.files[0]);

	}

}
