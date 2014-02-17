import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

# Create normal channel.
# XCH:'playtime' ==> hellow
chnl_normal = connection.channel()
chnl_normal.confirm_delivery()
chnl_normal.queue_declare(queue='hellow', durable=True)
chnl_normal.exchange_declare(exchange='playtime', exchange_type='direct')
chnl_normal.queue_bind(exchange='playtime', queue='hellow') # We need to bind this channel to an exchange, that will be used to transfer messages from THE delay queue.

# Create our delay channel.
# MX:''			==> hello_delay_2 ==> (MX:'playtime', route_key: 'hellow')
# 'hellow_delay_2' ==> 
chnl_delay = connection.channel()
chnl_delay.confirm_delivery()
chnl_delay.queue_declare(queue='hello_delay_2', durable=True,  arguments={ # This is where we declare the delay, and routing for our delay channel.
  'x-message-ttl' : 5000, # Delay until the message is transferred in milliseconds.
  'x-dead-letter-exchange' : 'playtime', # Exchange used to transfer the message from A to B.
  'x-dead-letter-routing-key' : 'hellow' # Name of the queue we want the message transferred to.
})

chnl_delay.basic_publish(exchange='',
                      routing_key='hello_delay_2',
                      body="test",
                      properties=pika.BasicProperties(delivery_mode=2))

print " [x] Sent"
