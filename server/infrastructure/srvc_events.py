from __future__ import absolute_import
from celery import Celery
from kombu  import Exchange, Queue



class HTRouter(object):
	def route_for_task(self, task, args=None, kwargs=None):
		print 'task_name: ' + str(task)
		return {'exchange': 'exec', 'exchange_type':'direct', 'routing_key':'dflt'}

mngr = Celery('event_manager')


# HeroTime defined config. options
TTL_1000 = { 'x-message-ttl': '1000' }
DLX_OPTS = {
    'x-dead-letter-exchange': 'exec',
	'x-dead-letter-routing-key': 'dflt',
}


rmqx_delayed = Exchange('DLXH', type='direct', arguments=DLX_OPTS)
rmqx_execute = Exchange('exec', type='direct')

mngr.conf.update(
	# where event/messages are sent to become tasks 
	BROKER_URL = 'amqp://guest:guest@darknight.local:5672/',
	CELERY_CREATE_MISSING_QUEUES = True,
	CELERY_INCLUDE = ['server.infrastructure.tasks'],

	# where task results are stored (could also be Redis)
	CELERY_RESULT_BACKEND = 'amqp://guest:guest@darknight.local:5672/',
	CELERY_RESULT_EXCHANGE = 'CAH_results',
	CELERY_RESULT_EXCHANGE_TYPE = 'direct',
	CELERY_RESULT_SERIALIZER	= 'json',
	CELERY_RESULT_PERSISTENT	= True,

	CELERY_TASK_RESULT_EXPIRES='3600',
	CELERY_TASK_SERIALIZER='json',

	CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content

	CELERY_DIRECT_STDOUTS_LEVEL = 'DEBUG',
	CELERY_TIMEZONE = 'America/Los_Angeles',
	CELERY_ENABLE_UTC = True,

	CELERY_DEFAULT_QUEUE		 = 'dflt',
	CELERY_DEFAULT_ROUTING_KEY	 = 'dflt',
	CELERY_DEFAULT_EXCHANGE		 = 'exec',
	CELERY_DEFAULT_EXCHANGE_TYPE = 'direct',

	CELERY_QUEUES = (
		Queue('dflt',	rmqx_execute,	routing_key='dflt'),
		Queue('h00',	rmqx_delayed,   routing_key='h00', queue_arguments={'x-message-ttl': 60}),
		Queue('h04',	rmqx_delayed,   routing_key='h04', queue_arguments={'x-message-ttl': 240}),
		Queue('h08',	rmqx_delayed,   routing_key='h08', queue_arguments={'x-message-ttl': 480}),
		Queue('h12',	rmqx_delayed,   routing_key='h08', queue_arguments={'x-message-ttl': 720}),
		Queue('h16',	rmqx_delayed,   routing_key='h16', queue_arguments={'x-message-ttl': 960}),
		Queue('h20',	rmqx_delayed,   routing_key='h20', queue_arguments={'x-message-ttl': 1200}),
	),

	CELERY_ROUTES = (HTRouter(),)
)
