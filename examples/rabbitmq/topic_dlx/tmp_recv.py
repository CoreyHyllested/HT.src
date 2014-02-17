import pika
import sys, time, random

#http://www.rabbitmq.com/tutorials/tutorial-four-python.html
#python recv_logs_topic.py "#"							// receive all logs
#python recv_logs_topic.py "kern.*"						// receive all logs from "kern"
#python recv_logs_topic.py "*.critical"					// receive all logs 'about' "critical"
#python recv_logs_topic.py "kern.*" ""*.critical"		// multiple bindings

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

print ' [*] Waiting for logs. To exit press CTRL+C'

def callback(ch, method, properties, body):
	print " [x] Received %r: %r" % (method.routing_key, body,)
	if random.random() < 0.5:
		print " [x] ack and sleep (5), should Timeout?"
		ch.basic_ack(delivery_tag = method.delivery_tag)
	else:
		print " [x] reject purposely, do not requeue"
		ch.basic_reject(delivery_tag = method.delivery_tag, requeue=False)
	print " [x] Done, method.delivery_tag = " + str(method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='hellow')
channel.start_consuming()

