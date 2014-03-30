	// If ESC is pressed, close all modal windows
	$(document).keyup(function(e) {
		if (e.keyCode == 27) {
			if ($('.alertWindowWrap').hasClass('alertWindowWrapOn') &&
				$('.alertWindow').hasClass('alertWindowOn')) {
					closeAlertWindow();
			}
		}
	});

	function searchBar() {
		var x=document.forms["srchForm"]["search"].value;
		if (x==null || x=="") { return false; }
		return true;
	}

	// Modal windows: Open
	function openAlertWindow(text) {
		$('.alertWindowWrap').toggleClass('alertWindowWrapOn');
		$('.alertWindow').toggleClass('alertWindowOn');
		$('.alertMessage').html(text);
		$('.alertOverlay').toggleClass('alertOverlayOn');
		return false;
	}

	// Modal windows: Close
	function closeAlertWindow() {
		$('.alertOverlay').toggleClass('alertOverlayOn');
		$('.alertWindowWrap').toggleClass('alertWindowWrapOn');
		$('.alertWindow').toggleClass('alertWindowOn');
		$('.alertMessage').html('');
		return false;
	}