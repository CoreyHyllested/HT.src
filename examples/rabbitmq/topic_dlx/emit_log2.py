import pika
import sys, logging
logging.getLogger('pika').setLevel(logging.DEBUG)

# connect to RabbitMQ.
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

# create chnl, topic_log xchange
channel = connection.channel()
channel.confirm_delivery()
channel.exchange_declare(exchange='topic_logs', exchange_type='topic')
channel.queue_declare(queue='hello', durable=True)
channel.queue_bind(exchange='topic_logs', queue='hello') # We need to bind this channel to an exchange, that will be used to transfer messages FROM the delay queue.



routing_topic = sys.argv[1] if (len(sys.argv) > 1) else 'anonymous.info'
message       = ' '.join(sys.argv[2:]) or "Hello World!"
channel.basic_publish(exchange='topic_logs', routing_key=routing_topic, body=message, properties=pika.BasicProperties(delivery_mode=2,))

# close re-srcs
print " [x] Sent %r:%r" % (routing_topic, message)
connection.close()








# Create our delay channel.
delay_channel = connection.channel()
delay_channel.confirm_delivery()
# This is where we declare the delay, and routing for our delay channel.
delay_channel.queue_declare(queue='hello_delay', durable=True,  arguments={
  'x-message-ttl' : 5000, # Delay until the message is transferred in milliseconds.
  'x-dead-letter-exchange' : 'topic_logs', # Exchange used to transfer the message from A to B.
  'x-dead-letter-routing-key' : 'hello' # Name of the queue we want the message transferred to.
})

delay_channel.basic_publish(exchange='',
                      routing_key='hello_delay',
                      body="test",
                      properties=pika.BasicProperties(delivery_mode=2))

print " [x] Sent"
