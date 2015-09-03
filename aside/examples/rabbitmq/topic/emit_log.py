import pika
import sys, logging
logging.getLogger('pika').setLevel(logging.DEBUG)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='topic_logs', exchange_type='topic')
routing_topic = sys.argv[1] if (len(sys.argv) > 1) else 'anonymous.info'
message       = ' '.join(sys.argv[2:]) or "Hello World!"
channel.basic_publish(exchange='topic_logs', routing_key=routing_topic, body=message, properties=pika.BasicProperties(delivery_mode=2,))
print " [x] Sent %r:%r" % (routing_topic, message)
connection.close()





