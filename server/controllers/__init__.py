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


import re, json
import urllib, urllib2

from pprint import pprint as pp
from datetime import timedelta, datetime as dt
from flask import request
from flask.ext.mail import Message
from flask.sessions import SessionInterface, SessionMixin
from server import sc_server
from server.infrastructure.tasks  import *
from server.infrastructure import errors
from server.models import *
from server.controllers.annotations import *
from server.controllers.authorize	import *
from server.controllers.forms		import *
from server.controllers.database	import *
from string import Template
from sqlalchemy     import distinct, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, aliased
from werkzeug.security       import generate_password_hash, check_password_hash
from werkzeug.datastructures import CallbackDict



def ht_get_active_author_reviews(profile):
	prof_reviews = htdb_get_composite_reviews(profile)
	active_reviews = ht_filter_composite_reviews(prof_reviews,	 filter_by='ACTIVE', profile=profile, dump=False)
	author_reviews = ht_filter_composite_reviews(active_reviews, filter_by='AUTHORED', profile=profile, dump=False)
	print 'ht_get_active_reviews() \ttotal:', len(prof_reviews), '\tactive:', len(active_reviews), '\tactive_authored:', len(author_reviews)
	return author_reviews




def ht_create_search_object(hashmap, mentor_prof_id, filtered_results):
	mentor = hashmap[mentor_prof_id]
	filtered_results.append(mentor[0])

	lesson_hits = []
	total_score = mentor[0].prof_score

	# add lessons as appropriate
	for lesson in mentor:
		if (lesson.less_score > 0):
			total_score = total_score + lesson.less_score
			lesson_hits.append(lesson)

	lesson_hits.sort(key=lambda x: x.less_score, reverse=True)
	lesson_hits = lesson_hits[0:3]
	setattr(mentor[0], 'lesson_hits', lesson_hits)
	setattr(mentor[0], 'total_score', total_score)
	print '\tht_score_mentor: Profile[' + str(mentor[0].prof_score) + '|' + str(total_score) + ']\t'+ mentor[0].Profile.prof_name  + '\t' + str(len(lesson_hits))





def ht_score_search_results(composite_lesson, keywords, hashmap):
	less_score = 0
	prof_score = 0

	for keyword in keywords:
		if (keyword in composite_lesson.Profile.prof_name.lower()):
			prof_score = prof_score + 1
		if (keyword in composite_lesson.Profile.headline.lower()):
			prof_score = prof_score + 1
		if (keyword in composite_lesson.Profile.prof_bio.lower()):
			prof_score = prof_score + 1
		if (keyword in composite_lesson.lesson.lesson_title.lower()):
			less_score = less_score + 1
		if (keyword in composite_lesson.lesson.lesson_description.lower()):
			less_score = less_score + 1

	setattr(composite_lesson, 'comp_score', (prof_score + less_score))
	setattr(composite_lesson, 'prof_score', prof_score)
	setattr(composite_lesson, 'less_score', less_score)

	if ((prof_score + less_score) > 0):
		# only add to map if at least one (profile/lesson) gets a hit.
		lesson_list = hashmap.get(composite_lesson.Profile.prof_id, [])
		lesson_list.append(composite_lesson)
		hashmap[composite_lesson.Profile.prof_id] = lesson_list

	print '\tht_score_lesson [' + str(less_score) + '|' + str(prof_score) + ']\t' + composite_lesson.Profile.prof_name, '\t', composite_lesson.lesson.lesson_title




def ht_filter_images(image_set, filter_by='VISIBLE', dump=False):
	images = []
	if (filter_by == 'VISIBLE'):
		images = filter(lambda img: (img.img_flags & IMG_STATE_VISIBLE), image_set)
	else:
		print '\t\t YOU DID NOT USE A VALID FILTER NAME'
	return images



def ht_filter_composite_reviews(review_set, filter_by='REVIEWED', profile=None, dump=False):
	reviews = []
	if (filter_by == 'REVIEWED'):
	#	print 'Searching review_set for reviews of', profile.prof_name, profile.prof_id
		reviews = filter(lambda r: (r.Review.prof_reviewed == profile.prof_id), review_set)
	elif (filter_by == 'AUTHORED'):
	#	print 'Searching review_set for reviews authored by', profile.prof_name, profile.prof_id
		reviews = filter(lambda r: (r.Review.prof_authored == profile.prof_id), review_set)
	elif (filter_by == 'VISIBLE'):
	#	print 'Searching review_set for reviews marked as visible'
		reviews = filter(lambda r: (r.Review.rev_status & REV_STATE_VISIBLE), review_set)
	elif (filter_by == 'ACTIVE'):
		reviews = filter(lambda r: (r.Review.rev_status & REV_STATE_CREATED), review_set)
	else:
		print '\t\t YOU SWUNG AND MISSED THE FILTER NAME'

	if (dump):
		print '\t\tfilter review_set by %s, by %s [%s]' % (filter_by, profile.prof_name, str(profile.prof_id)), '\tREVIEW SET: ', len(review_set), "=>", len(reviews)
		for r in reviews:
			# see htdb_get_composite_reviews() for object description.
			print '\t\t', r.user.prof_name, 'bought', r.hero.prof_name, 'on', r.Review.review_id, '\t', r.Review.rev_flags, '\t', r.Review.appt_score
	return reviews



def sc_update_account(uid, current_pw, new_pass=None, new_mail=None, new_status=None, new_secq=None, new_seca=None, new_name=None):
	return modifyAccount(uid, current_pw, new_pass, new_mail, new_status, new_secq, new_seca, new_name)


def modifyAccount(uid, current_pw, new_pass=None, new_mail=None, new_status=None, new_secq=None, new_seca=None, new_name=None):
	print uid, current_pw, new_pass, new_mail, new_status, new_secq, new_seca, new_name
	
	ba = Account.query.filter_by(userid=uid).all()[0]

	if (not check_password_hash(ba.pwhash, current_pw)):
		raise PasswordError(uid)

	if (new_pass != None):
		print "updating hash", ba.pwhash, "to", new_pass, generate_password_hash(new_pass)
		ba.pwhash = generate_password_hash(new_pass)

	if (new_mail != None):
		print "update email", ba.email, "to", new_mail
		ba.email = new_mail

	if (new_name != None):
		print "update name", ba.name, "to", new_name
		ba.name = new_name

	try:
		sc_server.database.session.add(ba)
		sc_server.database.session.commit()
	except Exception as e:
		sc_server.database.session.rollback()
		return False, e
	return True, True



def ht_assign_msg_threads_to_mbox(mbox_profile_id, msg_threads):
	inbox = []
	archive = []

	for thread in msg_threads:
		if (mbox_profile_id == thread.UserMessage.msg_to):
			thread_partner = Profile.get_by_prof_id(thread.UserMessage.msg_from)
			mbox = archive if (thread.UserMessage.msg_flags & MSG_STATE_RECV_ARCHIVE) else inbox
		elif (mbox_profile_id == thread.UserMessage.msg_from):
			thread_partner = Profile.get_by_prof_id(thread.UserMessage.msg_to)
			mbox = archive if (thread.UserMessage.msg_flags & MSG_STATE_SEND_ARCHIVE) else inbox
		else:
			print 'Major error.  profile_id didn\'t match to or from'
			continue
		setattr(thread, 'thread_partner', thread_partner)
		mbox.append(thread)

	return (inbox, archive)




def ht_create_avail_timeslot(profile):
	avail = None
	try:
		avail = Availability(profile)
		print 'ht_create_avail_timeslot: creating timeslot.'
		sc_server.database.session.add(avail)
		sc_server.database.session.commit()
	except IntegrityError as ie:
		print 'ht_create_avail_timeslot: ERROR ie:', ie
		sc_server.database.session.rollback()
	except Exception as e:
		print 'ht_create_avail_timeslot: ERROR e:', type(e), e
		sc_server.database.session.rollback()
	return avail



def htdb_get_lesson_images(lesson_id):
	try:
		lesson_images = sc_server.database.session.query(LessonImageMap)				\
						.filter(LessonImageMap.map_lesson == lesson_id)	\
						.order_by(LessonImageMap.map_order).all()
	except Exception as e:
		print type(e), e
	return lesson_images





#################################################################################
### DEPRECATED FUNCTIONS ########################################################
#################################################################################

@deprecated
def ht_create_account(name, email, passwd, ref_id):
	return sc_create_account(name, email, passwd, ref_id)

@deprecated
def ht_create_account_with_oauth(name, email, oa_provider, oa_data):
	return sc_create_account_with_oauth(name, email, oa_provider, oa_data)

@deprecated
def ht_get_unread_messages(profile):
	return sc_get_unread_messages(profile)

@deprecated
def ht_get_thread_messages(profile):
	return sc_get_thread_messages(profile)

@deprecated
def htdb_get_composite_messages(profile):
	return sc_get_composite_messages(profile)



#################################################################################
### HELPER FUNCTIONS ############################################################
#################################################################################

def get_geolocation_from_ip(ip=None):
	if (ip is None): ip = request.remote_addr

	# find IPV4 addrs. http://www.shellhacks.com/en/RegEx-Find-IP-Addresses-in-a-File-Using-Grep
	pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
	if not re.match(pattern, ip):
		return dict()

	# this was hanging.... recheck to make sure it works
	ip = 'google.com'
	ip_geo_url= 'http://freegeoip.net/json/' + str(ip)
	print ip_geo_url
	return json.loads((urllib.urlopen(ip_geo_url)).read())


def sc_print_timedelta(td):
	if (td.days >= 9):
		return 'more than a week'
	if (td.days >= 6):
		return 'about a week'
	elif (td.days >=2):
		return str(td.days) + ' days'
	elif (td.days == 1):
		return 'one day'
	else:
		return str(td.seconds / 3600) + ' hours'


def get_day_string(day):
	d = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
	return d[day]


def display_lastmsg_timestamps(msg, prof_id, all_messages):
	#print 'For Thread ', msg.UserMessage.msg_thread, msg.UserMessage.msg_subject[:20]
	thread_msgs = filter(lambda cmsg: (cmsg.UserMessage.msg_thread == msg.UserMessage.msg_thread), all_messages)
	thread_msgs.sort(key=lambda cmsg: (cmsg.UserMessage.msg_created))
	#for msg in thread_msgs:
	#	ts_open = msg.UserMessage.msg_opened.strftime('%b %d %I:%M:%S') if msg.UserMessage.msg_opened is not None else str('Unopened')
	#	print '\t Sorted [%s|%s] %r' % (msg.UserMessage.msg_thread, msg.UserMessage.msg_parent, ts_open)
	setattr(msg, 'lastmsg', thread_msgs[-1].UserMessage)
	#setattr(msg, 'lastmsg_sent', thread_msgs[-1].UserMessage.msg_created)
	#setattr(msg, 'lastmsg_open', thread_msgs[-1].UserMessage.msg_opened)
	#setattr(msg, 'lastmsg_to',   thread_msgs[-1].msg_to)

