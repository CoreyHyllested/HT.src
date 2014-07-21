$(document).ready(function() {

	/* When visible 'Choose File...' is clicked, activate hidden 'Browse...' */
	$("#editChooseImage").click(function() {
   		$("#change-photo-button").click();
	});

	/* When the profile pic is clicked, activate hidden 'Browse...' */
	$("#profile_img").click(function() {
   		$("#change-photo-button").click();
	});


	$("#edit-save-wrap").click(function () {
		var fd = new FormData($('#editform')[0]);
		fd.append('csrf_token', $('#csrf_token').val())
		fd.append('edit_name',     $('#edit_name').val())
		fd.append('edit_rate',     $('#edit_rate').val())
		fd.append('edit_headline', $('#edit_headline').val())
		fd.append('edit_location', $('#edit_location').val())
		fd.append('edit_industry', $('#edit_industry').val())
		fd.append('edit_bio',      $('#edit_bio').val())
		fd.append('edit_url',      $('#edit_url').val())
		fd.append('edit_photo',    $('#edit_photo').val())

		var xhr = new XMLHttpRequest();
		xhr.open('post', "/edit", true);
		xhr.send(fd)

		//catch response.  make any modificaitons.
		xhr.onreadystatechange = function(e) {
			if (4 == this.readyState) {
				if (this.status == 200) {
					console.log(['xhr post complete', e]);
					console.log(xhr.responseText);
					rc = JSON.parse(xhr.responseText);
					openAlertWindow("Success: " + rc['usrmsg'])
				} else {
					console.log(['xhr post complete', e]);
					rc = JSON.parse(xhr.responseText);
					openAlertWindow("Failure: " + rc['usrmsg'])
				}
			}
		};

		return false;
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
