import pika
import sys, time

#http://www.rabbitmq.com/tutorials/tutorial-four-python.html

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='direct_logs', type='direct')

queue      = channel.queue_declare(exclusive=True)
queue_name = queue.method.queue 

severities = sys.argv[1:]
if not severities:
		print >> sys.stderr, "Usage: %s [info] [warn] [error]" % (sys.argv[0],)
		sys.exit(1)

# create relationship between exchange / queue

# allow channel to bind use different routing_keys for the same queue
for severity in severities:
	channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key=severity)

print ' [*] Waiting for messages. To exit press CTRL+C'

def callback(ch, method, properties, body):
	print " [x] Received %r: %r" % (method.routing_key, body,)
	time.sleep( body.count('.') )
	print " [x] Done, method.delivery_tag = " + str(method.delivery_tag)
	#ch.basic_ack(delivery_tag = method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name, no_ack=True)
channel.start_consuming()

