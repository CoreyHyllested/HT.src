	// If ESC is pressed, close all modal windows
	$(document).keyup(function(e) {
		if (e.keyCode == 27) {
			if ($('.alertWindowWrap').hasClass('alertWindowWrapOn') &&
				$('.alertWindow').hasClass('alertWindowOn')) {
					closeAlertWindow();
			} else if ($('.modalWindowWrap').hasClass('modalWindowWrapOn') &&
				$('.modalWindow').hasClass('modalWindowOn')) {
					closeModalWindow();
			}
		}
	});


	// Alert windows: Open
	function openAlertWindow(text) {
		$('.alertWindowWrap').toggleClass('alertWindowWrapOn');
		$('.alertWindow').toggleClass('alertWindowOn');
		$('.alertMessage').html(text);
		$('.alertOverlay').toggleClass('alertOverlayOn');
		return false;
	}

	// Alert windows: Close
	function closeAlertWindow() {
		$('.alertOverlay').toggleClass('alertOverlayOn');
		$('.alertWindowWrap').toggleClass('alertWindowWrapOn');
		$('.alertWindow').toggleClass('alertWindowOn');
		$('.alertMessage').html('');
		return false;
	}

	// Modal windows: Open
	function openModalWindow(url, element, dataStr) {
		dataObj = JSON.parse(dataStr);
		
		$.each(dataObj, function(key, value){
		    console.log("dataObj: "+ key, value);
		});

		$('.modalWindowWrap').toggleClass('modalWindowWrapOn');
		$('.modalWindow').toggleClass('modalWindowOn');

		// TODO: modify the next line to pass data variables.
		// Something like $('.modalContent').load(url + " " + element, foo=bar);
		// Or $('.modalContent').load(url + " " + element, {foo:bar, foo2:bar2});

		$('.modalContent').load(url + " " + element);
		$('.modalOverlay').toggleClass('modalOverlayOn');
		return false;
	}

	// Modal windows: Close
	function closeModalWindow() {
		$('.modalOverlay').toggleClass('modalOverlayOn');
		$('.modalWindowWrap').toggleClass('modalWindowWrapOn');
		$('.modalWindow').toggleClass('modalWindowOn');
		$('.modalContent').html('');
		return false;
	}