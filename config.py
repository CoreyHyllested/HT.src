import os

CSRF_ENABLED = True
SECRET_KEY = "\xd8\x84.\xdbfk\x14]\x86\x10\x89\xbf\xcb\x04a\xd6'\xa7}\xc2\x019\x84\xc5"
SQLALCHEMY_DATABASE_URI = 'postgresql://ezjlivdbtrqwgx:lM5sTTQ8mMRM7CPM0JrSb50vDJ@ec2-54-235-70-146.compute-1.amazonaws.com:5432/d673en78hg143l'
#SQLALCHEMY_DATABASE_URI = 'postgresql://aysevvyxmqbmhd:Vpt-i6asNIpgkv96PZQ2pLWOqv@ec2-54-225-101-18.compute-1.amazonaws.com:5432/d87o5r1so43ija'

#SQLALCHEMY_DATABASE_URI = 'sqlite:///ht.db'
DATABASE_QUERY_TIMEOUT = 1.0 

# HeroTime definitions
HT_UPLOAD_DIR='/tmp/ht_upload/'
HT_IMAGES_EXT=set(['png', 'jpg', 'jpeg', 'bmp'])

# gz Compression Opts. 
#COMPRESS_MIN_SIZE=500
#COMPRESS_DEBUG=True

# https://redistogo.com/instances/292777?language=en
# RedisToGo.com :: herotime/'coming in Nov 2013'/corey@herotime.co
#REDIS_URL='redis://redistogo:5f32a6ca8a924e770643fdcc192c6320@grideye.redistogo.com:9056/'
REDIS_URL='redis://ht-redis.h6fyv6.0001.use1.cache.amazonaws.com:6379/'
REDIS_URL='redis://redistogo:5f32a6ca8a924e770643fdcc192c6320@grideye.redistogo.com:9056/'

MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'ht.accnts@gmail.com'
MAIL_PASSWORD = 'coming in Nov 2013'

S3_KEY = 'AKIAIVMHLA4ZZXB5NIRQ'
S3_BUCKET = 'htfileupload'
S3_SECRET = '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'
S3_SERVER = 'htfileupload.s3-website-us-west-1.amazonaws.com'	
S3_DIRECTORY = '/htfileupload/'

LINKEDIN_KEY="ri7ghzey680z"
LINKEDIN_SEC="LcHMnsf9vVqUg8rE"

OPENID_PROVIDERS = [
	{ 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
	{ 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
	{ 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
	{ 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
	{ 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]



