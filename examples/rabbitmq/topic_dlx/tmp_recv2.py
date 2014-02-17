import pika
import sys, time, random

#http://www.rabbitmq.com/tutorials/tutorial-four-python.html
#python recv_logs_topic.py "#"							// receive all logs
#python recv_logs_topic.py "kern.*"						// receive all logs from "kern"
#python recv_logs_topic.py "*.critical"					// receive all logs 'about' "critical"
#python recv_logs_topic.py "kern.*" ""*.critical"		// multiple bindings

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.basic_qos(prefetch_count=1)

print ' [*] Waiting for logs. To exit press CTRL+C'

def callback(ch, method, properties, body):
	print " [x] Received %r: %r" % (method.routing_key, body,)
	ch.basic_ack(delivery_tag = method.delivery_tag)
	print " [x] Done, method.delivery_tag = " + str(method.delivery_tag)


channel.basic_consume(callback, queue='hello_delay_2')
channel.start_consuming()

