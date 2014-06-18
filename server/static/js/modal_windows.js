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
		console.log("dataStr: "+dataStr);
		dataObj = JSON.parse(dataStr);
		$.each(dataObj, function(key, value){
		    console.log("dataObj: "+ key, value);
		});
		var encodedData = $.param(dataObj);
		console.log("encodedData: "+ encodedData);

		$('.modalWindowWrap').toggleClass('modalWindowWrapOn');
		$('.modalWindow').toggleClass('modalWindowOn');
		$('.modalWindowClose').toggleClass('modalWindowCloseOn');		
		$('.modalContent').load(url+"?"+encodedData + " " + element);
		$('.modalOverlay').toggleClass('modalOverlayOn');
		return false;
	}

	// Modal windows: Close
	function closeModalWindow() {
		$('.modalOverlay').toggleClass('modalOverlayOn');
		$('.modalWindowWrap').toggleClass('modalWindowWrapOn');
		$('.modalWindowClose').toggleClass('modalWindowCloseOn');		
		$('.modalWindow').toggleClass('modalWindowOn');
		$('.modalContent').html('');
		return false;
	}