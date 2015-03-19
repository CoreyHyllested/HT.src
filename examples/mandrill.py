import mandrill
 
API_KEY = 'Fc1-NkxSROn715kzsldP8A'
 
 
def send_mail(template_name, email_to, context):
	try: 
		mandrill_client = mandrill.Mandrill(API_KEY)
		message = {
			'to': [],
			'global_merge_vars': []
		}
		for em in email_to:
			message['to'].append({'email': em})
	 
		for k, v in context.iteritems():
			message['global_merge_vars'].append(
				{'name': k, 'content': v}
			)
		print 'send template' + str(template_name)
		mandrill_client.messages.send_template(template_name, [], message)
	except Exception as e:
		print e, type(e)
	 


send_mail('invite-a-friend', ["corey.hyllested@gmail.com"], context={'Name': "Corey Andrew-Trapper Hyllested"})
