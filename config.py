#################################################################################
# Copyright (C) 2013 - 2014 Insprite, LLC.
# All Rights Reserved.
# 
# All information contained is the property of Insprite, LLC.  Any intellectual 
# property about the design, implementation, processes, and interactions with 
# services may be protected by U.S. and Foreign Patents.  All intellectual 
# property contained within is covered by trade secret and copyright law.   
# 
# Dissemination or reproduction is strictly forbidden unless prior written 
# consent has been obtained from Insprite, LLC.
#################################################################################


import os

HT_BASEDIR	= os.path.abspath(os.path.dirname(__file__))
LOCAL_MODE	= os.environ.get("LOCAL", None)


class Config:
	# Flask Config Options
	CSRF_ENABLED = True
	SECRET_KEY = "\xd8\x84.\xdbfk\x14]\x86\x10\x89\xbf\xcb\x04a\xd6'\xa7}\xc2\x019\x84\xc5"

	SQLALCHEMY_DATABASE_URI = 'postgresql://htdb:passw0rd@beta3.cesf5wqzwzr9.us-east-1.rds.amazonaws.com:5432/htdb'
	SQLALCHEMY_MIGRATE_REPO = HT_BASEDIR + '/database/'
	DATABASE_QUERY_TIMEOUT = 1.0

	HT_UPLOAD_DIR='/tmp/ht_upload/'
	HT_IMAGES_EXT=set(['png', 'jpg', 'jpeg', 'bmp'])

	JSFILTER=None

	S3_KEY = 'AKIAIVMHLA4ZZXB5NIRQ'
	S3_BUCKET = 'htfileupload'
	S3_SECRET = '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'
	S3_SERVER = 'htfileupload.s3-website-us-west-1.amazonaws.com'
	S3_DIRECTORY = '/htfileupload/'


	STRIPE_PUBLIC =	'pk_test_d3gRvdhkXhLBS3ABhRPhOort'
	STRIPE_SECRET =	'sk_test_wNvqK0VIg7EqgmeXxiOC62md'

	LINKEDIN_KEY = 'ri7ghzey680z'
	LINKEDIN_SEC = 'LcHMnsf9vVqUg8rE'

	FACEBOOK_APP_ID='243739575814575'
	FACEBOOK_APP_SEC='c08f6c6f920b6cac0a3743822483f7bf'

	@staticmethod
	def init_app(app):
		print 'SQLALCHEMY_DB: ' + str(SQLALCHEMY_DATABASE_URI)
		pass



class DevelopmentConfig(Config):
	# https://redistogo.com/instances/292777?language=en
	# RedisToGo.com :: herotime/'coming in Nov 2013'/corey@herotime.co
	REDIS_URL='redis://redistogo:5f32a6ca8a924e770643fdcc192c6320@grideye.redistogo.com:9056/'




class DevelMoneyConfig(Config):
	# https://redistogo.com/instances/292777?language=en
	# RedisToGo.com :: herotime/'coming in Nov 2013'/corey@herotime.co
	REDIS_URL='redis://redistogo:5f32a6ca8a924e770643fdcc192c6320@grideye.redistogo.com:9056/'
	STRIPE_PUBLIC =	'pk_live_uln2RsRFAILYDVG2ZMJj52JZ'
	STRIPE_SECRET = 'sk_live_PkVMnc27rXEeb63WxO514N9X'




class ProductionConfig(Config):
	# gz Compression Opts.
	#COMPRESS_MIN_SIZE=500
	#COMPRESS_DEBUG=True

	SQLALCHEMY_DATABASE_URI = 'postgresql://htdb:passw0rd@htdb.cesf5wqzwzr9.us-east-1.rds.amazonaws.com:5432/htdb'
	REDIS_URL='redis://ht-redis.h6fyv6.0001.use1.cache.amazonaws.com:6379/'
	JSFILTER='jsmin'



class TestingConfig(Config):
	TESTING = True
	WTF_CSRF_ENABLED = False	# Boo. Hiss.  But means we don't have to parse the page much.
	REDIS_URL='redis://redistogo:5f32a6ca8a924e770643fdcc192c6320@grideye.redistogo.com:9056/'

	# maybe we don't use this
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + HT_BASEDIR + '/insprite.db'
	print 'SQLALCHEMY_DB: ' + str(SQLALCHEMY_DATABASE_URI)

	def __init__ (self):
		print 'creating testing config'



server_configuration = {
	'default'		: DevelopmentConfig,

	'development'	: DevelopmentConfig,
	'devel_money'	: DevelMoneyConfig,
	'production'	: ProductionConfig,
	'testing'		: TestingConfig
}
