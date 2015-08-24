################################################################################
# Copyright (C) 2015 Soulcrafting
# All Rights Reserved.
#
# All information contained is the property of Soulcrafting. Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents.  All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Soulcrafting.
#################################################################################

import os, boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from StringIO import StringIO
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ht_create_image(profile, image_data, comment=None):
	print 'upload()\tht_create_image()\tenter'
	imgid = secure_filename(hashlib.sha1(image_data).hexdigest()) + '.jpg'
	image = Image.get_by_id(imgid)
	if (image is None):
		print 'upload()\tht_image_create\t image does not exist.  Create it.'
		# image doesn't exist. Create and upload to S3
		image = Image(imgid, profile.prof_id, comment)
		try:
			ht_upload_image_to_S3(image, image_data)
			database.session.add(image)
			database.session.commit()
		except IntegrityError as ie:
			# image already exists.
			print 'upload()\tht_image_create() funny seeing image already exist here.'
			print 'upload: exception', type(e), e
			database.session.rollback()
		except Exception as e:
			print 'upload: exception', type(e), e
			database.session.rollback()
	return image



def ht_upload_image_to_S3(image, image_data):
	f = open(os.path.join(sc_server.config['SC_UPLOAD_DIR'], image.img_id), 'w')
	f.write(image_data)
	f.close()

	print 'upload()\tupload_image_to_S3\tpush image to S3.'
	s3_con = boto.connect_s3(sc_server.config["S3_KEY"], sc_server.config["S3_SECRET"])
	s3_bkt = s3_con.get_bucket(sc_server.config["S3_BUCKET"])
	s3_key = s3_bkt.new_key(sc_server.config["S3_DIRECTORY"] + image.img_id)
	print 'upload()\tupload_image_to_S3\tcreated s3_key.'
	s3_key.set_contents_from_file(StringIO(image_data))

