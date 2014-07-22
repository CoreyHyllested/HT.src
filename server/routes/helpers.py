
def display_partner_message(msg, prof_id):
	display_prof = (prof_id == msg.UserMessage.msg_to) and msg.msg_from or msg.msg_to
	setattr(msg, 'display', display_prof)

