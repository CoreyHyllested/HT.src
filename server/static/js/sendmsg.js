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
					$(".messageThreadItemLoading").fadeIn();
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
	$('#sendMessage').on("click", sendmessage_js);
});
