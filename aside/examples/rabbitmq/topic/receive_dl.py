import pika
import time
 


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='dlx', exchange_type='direct')

queue_dl      = channel.queue_declare(queue='dl')
queue_dl_name = queue_dl.method.queue
channel.queue_bind(exchange='dlx', routing_key='task_queue', queue=queue_dl_name) # x-dead-letter-routing-key
 
print ' [*] Waiting for dead-letters. To exit press CTRL+C'
 
def callback(ch, method, properties, body):
    print " [x] %r" % (properties,)
    print " [reason] : %s : %r" % (properties.headers['x-death'][0]['reason'], body)
    ch.basic_ack(delivery_tag = method.delivery_tag)
 
channel.basic_consume(callback, queue=queue_dl_name)
channel.start_consuming()
