#!/usr/bin/env python
import pika
import uuid

class FibonacciRpcClient(object):
	def __init__(self):
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		self.channel = self.connection.channel()

		result = self.channel.queue_declare(exclusive=True)
		self.callback_queue = result.method.queue
		self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

	def on_response(self, ch, method, props, body):
		if self.corr_id == props.correlation_id:
			self.response = body

	def call(self, n):
		self.response = None
		self.corr_id = str(uuid.uuid4())
		self.channel.basic_publish(exchange='', routing_key='rpc_queue', properties=pika.BasicProperties(reply_to = self.callback_queue, correlation_id = self.corr_id,), body=str(n))
		while self.response is None:
			self.connection.process_data_events()
		return int(self.response)


fibonacci_rpc = FibonacciRpcClient()

print " [x] Requesting fib(70)"
response = fibonacci_rpc.call(70)
response = fibonacci_rpc.call(60)
response = fibonacci_rpc.call(50)
response = fibonacci_rpc.call(40)
response = fibonacci_rpc.call(25)
response = fibonacci_rpc.call(20)
response = fibonacci_rpc.call(10)
print " [.] Got %r" % (response,)
print " [x] Requesting fib(60)"
print " [.] Got %r" % (response,)
print " [x] Requesting fib(50)"
print " [.] Got %r" % (response,)
print " [x] Requesting fib(40)"
print " [.] Got %r" % (response,)
print " [x] Requesting fib(25)"
print " [.] Got %r" % (response,)
print " [x] Requesting fib(20)"
print " [.] Got %r" % (response,)
print " [x] Requesting fib(10)"
print " [.] Got %r" % (response,)
