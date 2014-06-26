function loadMessageThread(msg_thread_id) {
	var fd = {};
	fd.msg_thread_id = msg_thread_id;
	fd.csrf_token = "{{ csrf_token() }}";
	$.ajax({ url : "/message",
			 type : "POST",
			 data : fd,
			 success : function(data) {
				var page_content = $(data).find('.messageThreadItemContainer').html();
				var conversation_title = $(data).find('.messageThreadConvoTitle').html();
				var num_thread_messages = $(data).find('.messageThreadNumMessages').html();

				$('.messageThreadItemContainer').html(page_content);
				$('.inboxMessagesHeaderConvoTitle').html(conversation_title + " " + num_thread_messages);

			}
	});
}




function verify_email_js(e) {
	e.preventDefault();
	var fd = {};
	var challenge = $('#challenge').val();
	fd.email_addr = $('#set_input_email').val();
	fd.csrf_token = $('#csrf').val();
	fd.next_url   = $('#nexturl').val();

	$.each(fd, function(k, v) { console.log(k+ ": " + v); });
	$.ajax({ url : '/email/verify/'+challenge,
			 type : 'POST', 	
			 data : fd,
			 dataType: 'json',
			 success : function(data) { 
				 console.log ('in success');
				 console.log(data);
				 window.location.href = $('#nexturl').val();
				 return false; 
			 },
			 error: function(data) {
				 console.log ('in fail');
			 }
	});
	return false;
}



function send_verification_email() {
	console.log('send_verification_email()');
	var fd = {};
	fd.email_addr = $('#set_input_email').val();
	fd.csrf_token = $('#csrf').val();

	$.each(fd, function(k, v) { console.log(k+ ": " + v); });
	$.ajax({ url : '/email/request-verification/me',
			 type : 'POST',
			 data : fd,
			 success : function(data) {
				 console.log('sent verification emails');
			}
	});
}


function replyDOMUpdate(msg_thread_id) {

	var thisThreadElement = $('.thread[data-thread-id="' + msg_thread_id + '"]');
	if (thisThreadElement.find('div.threadRestore').length != 0) {
		// This is a thread moving from the archive to the inbox.
		thisThreadElement.children(".threadAction").removeClass("threadRestore").addClass("threadArchive").html('<a title="Archive Message" class="blend"><i class="fa fa-archive"></i></a>');
		$('.messageViewThreadRestore').hide();
		$('.messageViewThreadArchive').show();
		numInbox = ++numInbox;
		numArchived = --numArchived;
	}
	$('#inboxThreads li.thread').first().before(thisThreadElement);
}	



function archiveDOMUpdate(msg_thread_id) {

	var thisThreadElement = $('.thread[data-thread-id="' + msg_thread_id + '"]');
	thisThreadElement.children(".threadAction").removeClass("threadArchive").addClass("threadRestore").html('<a title="Restore Message" class="blend"><i class="fa fa-level-up"></i></a>');

	// Find where in the message list this ones goes chronologically
	var threadPlaced = 0;
	$('ul#archiveThreads li').each(function() {
		var thisTimestamp = parseInt($(this).data("timestamp"));
		var targetTimestamp = parseInt(thisThreadElement.data("timestamp"));
		if (thisTimestamp < targetTimestamp) {
			$(this).before(thisThreadElement);
			threadPlaced = 1;
			return false;
		}
	});

	// We archived the earliest message in the account
	if (threadPlaced == 0){
		$('ul#archiveThreads').append(thisThreadElement);
	}
}	

function restoreDOMUpdate(msg_thread_id) {

	var thisThreadElement = $('.thread[data-thread-id="' + msg_thread_id + '"]');
	thisThreadElement.children(".threadAction").removeClass("threadRestore").addClass("threadArchive").html('<a title="Archive Message" class="blend"><i class="fa fa-archive"></i></a>');

	// Find where in the message list this ones goes chronologically
	var threadPlaced = 0;
	$('ul#inboxThreads li').each(function() {
		var thisTimestamp = parseInt($(this).data("timestamp"));
		var targetTimestamp = parseInt(thisThreadElement.data("timestamp"));
		if (thisTimestamp < targetTimestamp) {
			$(this).before(thisThreadElement);
			threadPlaced = 1;
			return false;
		}
	});

	// We archived the earliest message in the account
	if (threadPlaced == 0){
		$('ul#inboxThreads').append(thisThreadElement);
	}
}	




function sendmessage_js(e) {
	var messageData = {};
	messageData.hp = $('#composeRecipientID').val();
	messageData.recipient_name = $('#composeRecipientName').val();
	messageData.msg = $('#composeBody').val();
	messageData.msg_thread = $('#msg_thread').val();
	messageData.msg_parent = $('#msg_parent').val();
	messageData.subject = $('#composeSubject').val();
	messageData.csrf_token = $('#csrf').val();
	messageData.next = $('#next').val();

	$.each(messageData, function(index, val) {
	    console.log(index + ": " + val);
	});

	$.ajax({
		url: '/sendmsg',
		method: 'post',
		data: messageData,
		dataType: 'json',
		success: function(response) {
			// console.log('AJAX Success.');
			if (response.valid == "true") {
				console.log('Success.');
				if (response.next == null) {
					if ($(".composeMessageStatus").length > 0) {
						$(".composeMessageStatus").html("Success! Next is not set.").show();
					}
					window.location.href = "/inbox";			
				} else if (response.next == "modal") { 
					// TODO - if we want to add estimated response time, this is where to do it.
					if ($(".composeMessageStatus").length > 0) {
						$(".composeMessageStatus").html("<span class='success'>Message successfully sent to "+messageData.recipient_name+" - Closing window...</span>").slideDown();
					}
					setTimeout(function() { closeModalWindow(); }, 2000);				
				} else if (response.next == "thread") { 
					// This is a reply to an existing message thread. 
					$(".messageThreadItemLoading").fadeIn();

					replyDOMUpdate(messageData.msg_thread);

					var num_thread_messages = $(".messageThread").data("threadNumMessages") + 1;
					$(".messageThread").data("threadNumMessages", num_thread_messages);
					$('.numThreadMessages').text("("+ num_thread_messages + " Messages)");
					$(".messageReplyBody").val('');
					$(".messageReplyStatus").html("<span class='success'>Message successfully sent to "+messageData.recipient_name+"</span>").fadeIn();
					setTimeout(function() {
						$('.messageReplyStatus').slideUp(1000);
					}, 2000 );
					$('.messageThreadContainer').load("/inbox/message/" + messageData.msg_thread + " .messageThread");	
				} else {
					if ($(".composeMessageStatus").length > 0) {
						$(".composeMessageStatus").html("<span class='success'>Message successfully sent to "+messageData.recipient_name+"</span>").slideDown();
					}
					setTimeout(function() { window.location.href = response.next; }, 10000);
				}
		    } else {
				$(".composeMessageStatus").html("<span class='error'>Sorry, something went wrong. Message not sent.</span>").slideDown();
				console.log ('Error - Valid not true');
		    }
		},
		error:function(response) {
			$(".composeMessageStatus").html("<span class='error'>Sorry, something went wrong. Message not sent.</span>").slideDown();
			console.log("Error - " + response.usrmsg);
		}
	});
	return false;
}

$(document).ready(function() {
	console.log('page ready');
	$('#rec_submit').on('click', verify_email_js);
	$('#rec_verify').on('click', send_verification_email);
	$('#sendMessage').on("click", sendmessage_js);
});
