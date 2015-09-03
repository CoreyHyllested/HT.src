#!/usr/bin/env python
import pika
import uuid

class RpcClient(object):
	def __init__(self):
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		self.chnl_normal = self.connection.channel()
		self.chnl_normal.confirm_delivery()
		self.chnl_normal.exchange_declare(exchange='task_x', exchange_type='direct')
		self.chnl_normal.queue_declare(queue='task_q', durable=True)
		self.chnl_normal.queue_bind(exchange='task_x', queue='task_q') # We bind this chnl to an exchange, that will be used to transfer messages FROM THE delay queue.



	def on_response(self, ch, method, props, body):
		print 'on_resp'
		if self.corr_id == props.correlation_id:
			print 'my ID = ' + str(self.corr_id)
			self.response = body
			print 'my resp = ' + body
			

	def call(self):
		self.chnl_delay  = self.connection.channel()
		self.chnl_delay.confirm_delivery()

		callback_q     = self.chnl_delay.queue_declare(exclusive=True)
		self.chnl_delay.basic_consume(self.on_response, no_ack=True, queue=callback_q.method.queue)


		self.tmp_queue = self.chnl_delay.queue_declare(durable=True, exclusive=True, arguments={ # This is where we declare the delay, and routing for our delay channel.
		  'x-dead-letter-exchange' : 'task_x', # Exchange used to transfer the message from A to B.
		  'x-dead-letter-routing-key' : 'task_q' # Name of the queue we want the message transferred to.
		})
	
		self.response = None
		self.corr_id  = str(uuid.uuid4())
		msg_prop = pika.BasicProperties(expiration='4000', delivery_mode=2,
										   reply_to=callback_q.method.queue,
										   correlation_id=self.corr_id)

		rc = self.chnl_delay.basic_publish(exchange='',
					                       routing_key=self.tmp_queue.method.queue,
		   				                   body="test this shit bitches ",
		               				       properties=msg_prop)
		print 'callback_q (exlcusive)'  + str(callback_q.method.queue)
		print 'temp_q (durable)'  + str(self.tmp_queue.method.queue)
		
		if rc:
			print "> sent msg, confirmed" 
			print rc
		else:
			print "> sent msg, unconfirmed" 

		print "# now wait for a response"
		while self.response is None:
			self.connection.process_data_events()
		self.connection.close()


rpc = RpcClient()
rpc.call()
