#################################################################################
# Copyright (C) 2015 Soulcrafting
# All Rights Reserved.
#
# All information contained is the property of Soulcrafting. Any intellectual
# property about the design, implementation, processes, and interactions with
# services may be protected by U.S. and Foreign Patents. All intellectual
# property contained within is covered by trade secret and copyright law.
#
# Dissemination or reproduction is strictly forbidden unless prior written
# consent has been obtained from Soulcrafting.
#################################################################################

import sys, os
import json
from pprint import pprint as pp


DIR_RAWHTML = '/data/raw/'
DIR_PROCESS	= '/data/process/'
DIR_MERGED	= '/data/process/merged/'
DIR_REVIEWS	= '/data/reviews/'
DIR_SOURCES	= '/data/sources/'


def safe_mkdir_local(path):
	directory = os.getcwd() + path
	safe_mkdir(directory)


def safe_mkdir(directory):
	if (os.path.exists(directory) == False):
		os.makedirs(directory)


def open_file(path_from_cwd):
	filename = os.getcwd() + path_from_cwd
	print 'creating file ' + str(filename)
	fp = open(filename, 'a+')
	return fp



def read_file(file_path, DEBUG=False):
	if (DEBUG): print 'opening file', file_path
	if (file_path[0] is not '/'):
		file_path = os.getcwd() + '/' + file_path

	fp = None
	if (DEBUG): print 'opening file', file_path
	try:
		fp = open(file_path)
		file_content = fp.read()
		if (DEBUG): print 'reading file ', len(file_content)
		json_content = json.loads(file_content)
		if (DEBUG): pp(json_content)
		#directory = data.get('directory', [])
		return json_content
	except Exception as e:
		print e
	finally:
		if (fp): fp.close()
	return { "data" : None }
	


def path_from_cwd_to(path_from_cwd):
	return os.getcwd() + path_from_cwd

def create_review(review_id):
	fn = '/data/reviews/' + review_id
	fp = open_file(fn)
	fp.truncate()
	return fp


def create_directories():
	safe_mkdir_local(DIR_RAWHTML)
	#safe_mkdir_local(DIR_REVIEWS)
	safe_mkdir_local(DIR_SOURCES)


def write_file(filename, content):
	fp = None
	try:
		fp = open(filename, 'w+')
		fp.truncate()
		fp.write(content)
	except Exception as e:
		print e
	finally:
		if (fp): fp.close()
	


def update(filename, content):
	fp = None
	try:
		fp = open(filename, 'w+')
		fp.truncate()
		fp.write(content)
	except Exception as e:
		print e
	finally:
		if (fp): fp.close()
	

