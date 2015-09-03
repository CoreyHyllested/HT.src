import pika
import sys, time

#http://www.rabbitmq.com/tutorials/tutorial-four-python.html
#python recv_logs_topic.py "#"							// receive all logs
#python recv_logs_topic.py "kern.*"						// receive all logs from "kern"
#python recv_logs_topic.py "*.critical"					// receive all logs 'about' "critical"
#python recv_logs_topic.py "kern.*" ""*.critical"		// multiple bindings

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

queue      = channel.queue_declare(exclusive=True)
queue_name = queue.method.queue 

bind_keys = sys.argv[1:]
if not bind_keys:
		print >> sys.stderr, "recv_logs_topic.py \"kern.*\"\t// receive all logs from \"kern\""
		print >> sys.stderr, "recv_logs_topic.py \"*.crit\"\t// receive all logs abt \"crit\""
		sys.exit(1)

# allow channel to bind use different routing_keys for the same queue
for bind_key in bind_keys:
	# create relationship between exchange / queue
	channel.queue_bind(exchange='topic_logs', queue=queue_name, routing_key=bind_key)

print ' [*] Waiting for logs. To exit press CTRL+C'

def callback(ch, method, properties, body):
	print " [x] Received %r: %r" % (method.routing_key, body,)
	time.sleep( body.count('.') )
	print " [x] Done, method.delivery_tag = " + str(method.delivery_tag)
	#ch.basic_ack(delivery_tag = method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=True)
channel.start_consuming()

