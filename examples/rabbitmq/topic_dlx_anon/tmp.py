import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

# Create normal channel.
# XCH:'ht_tasks' ==> hellow
chnl_normal = connection.channel()
chnl_normal.confirm_delivery()
chnl_normal.queue_declare(queue='task_q', durable=True)
chnl_normal.exchange_declare(exchange='task_x', exchange_type='direct')
chnl_normal.queue_bind(exchange='task_x', queue='task_q') # We need to bind this channel to an exchange, that will be used to transfer messages from THE delay queue.

# Create our delay channel; don't connect to anything.
# MX:''			==> hello_delay_3 ==> (MX:'ht_tasks', route_key: 'hellow')
# 'hellow_delay_2' ==> 
chnl_delay = connection.channel()
chnl_delay.confirm_delivery()
chnl_delay.queue_declare(queue='delay_q', durable=True,  arguments={ # This is where we declare the delay, and routing for our delay channel.
  'x-dead-letter-exchange' : 'task_x', # Exchange used to transfer the message from A to B.
  'x-dead-letter-routing-key' : 'task_q' # Name of the queue we want the message transferred to.
})

#msg_prop = pika.BasicProperties(delivery_mode=2, 'x-expires'=5000)
msg_prop = pika.BasicProperties(expiration='1000')
chnl_delay.basic_publish(exchange='',
                      routing_key='delay_q',
                      body="test this shit bitches",
                      properties=msg_prop)

print " [x] Sent"
