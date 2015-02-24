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
	function openModalWindow(url, element, dataStr, modalClass) {
		$('.modalOverlay').toggleClass('modalOverlayOn');
/*		$('.modalWindowWrap').showCloseWindowButton(); */
		$('.modalContent').load(url + " " + element);
		return false;
	}

	function showCloseWindowButton() {
		$('.modalWindowClose').show();
	}

	// Modal windows: Close
	function closeModalWindow() {
		$('.modalWindowClose').hide();
		$('.modalContent').html('');
		$( ".modalWindowWrap" ).css("opacity", 0);
		$('.modalOverlay').toggleClass('modalOverlayOn');
		
		return false;
	}
