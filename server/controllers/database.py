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

import os
from server import database
from server.models import *
from sqlalchemy.orm import aliased




#TODO change name.  sc_get_references.
def scdb_get_references(profile, dump=False):
	""" get all refreqs for 'profile'; disabled to remove BusinessReference """
	#references = sc_server.database.session.query(BusinessReference).filter(BusinessReference.br_bus_prof == profile.prof_id).all();
	#if (dump):
	#	for r in references: print '\tREF_REQ', r.br_uuid, ':', r.br_bus_prof, 'wants', r.br_req_mail
	return None #references


def sc_get_projects(profile):
	projects = database.session.query(Project)								\
							.filter(Project.account == profile.account)		\
							.all();
	return projects


def sc_get_composite_messages(profile):
	msg_from = aliased(Profile, name='msg_from')
	msg_to	 = aliased(Profile, name='msg_to')

	messages = database.session.query(UserMessage, msg_from, msg_to)																		\
							 .filter(or_(UserMessage.msg_to == profile.prof_id, UserMessage.msg_from == profile.prof_id))			\
							 .join(msg_from, msg_from.prof_id == UserMessage.msg_from)												\
							 .join(msg_to,   msg_to.prof_id   == UserMessage.msg_to).all();
	return messages


def sc_get_unread_messages(profile):
	all_msgs	= sc_get_composite_messages(profile)
	unread_msgs	= ht_filter_composite_messages(all_msgs, profile, filter_by='UNREAD')
	toProf_msgs = ht_filter_composite_messages(unread_msgs, profile, filter_by='RECEIVED', dump=False)
	return toProf_msgs


def sc_get_thread_messages(profile):
	all_msgs	= sc_get_composite_messages(profile)
	msg_threads	= ht_filter_composite_messages(all_msgs, profile, filter_by='THREADS')
	return msg_threads


def ht_filter_composite_messages(message_set, profile, filter_by='RECEIVED', dump=False):
	messages = []
	if (filter_by == 'RECEIVED'):
		#print 'Searching message_set for messages received by ', profile.prof_name, profile.prof_id
		messages = filter(lambda msg: (msg.UserMessage.msg_to == profile.prof_id), message_set)
	if (filter_by == 'SENT'):
		#print 'Searching message_set for messages sent by', profile.prof_name, profile.prof_id
		messages = filter(lambda msg: (msg.UserMessage.msg_from == profile.prof_id), message_set)
	if (filter_by == 'UNREAD'):
		#print 'Searching message_set for messages marked as unread'
		messages = filter(lambda msg: ((msg.UserMessage.msg_flags & MSG_STATE_LASTMSG_READ) == 0), message_set)
	if (filter_by == 'THREADS'):
		#print 'Searching message_set for messages marked as unread'
		messages = filter(lambda msg: ((msg.UserMessage.msg_thread == msg.UserMessage.msg_id) == 0), message_set)

	if (dump):
		#print 'Original set',  len(message_set), "=>", len(messages)
		for msg in messages:
			print msg.msg_from.prof_name, 'sent', msg.msg_to.prof_name, 'about', msg.UserMessage.msg_subject, '\t', msg.UserMessage.msg_flags, '\t', msg.UserMessage.msg_thread
	return messages



def htdb_get_composite_reviews(profile):
	hero = aliased(Profile, name='hero')
	user = aliased(Profile, name='user')
	meet = aliased(Meeting, name='meet')

	# COMPOSITE REVIEW OBJECT
	# OBJ.Review	# Review
	# OBJ.hero		# Profile of seller
	# OBJ.user		# Profile of buyer
	# OBJ.meet		# Meeting object
	# OBJ.display	# <ptr> Profile of other person (not me)

	all_reviews = database.session.query(Review, meet, hero, user).distinct(Review.review_id)											\
								.filter(or_(Review.prof_reviewed == profile.prof_id, Review.prof_authored == profile.prof_id))	\
								.join(meet, meet.meet_id == Review.rev_appt)													\
								.join(user, user.prof_id == Review.prof_authored)												\
								.join(hero, hero.prof_id == Review.prof_reviewed).all();
	map(lambda review: display_review_partner(review, profile.prof_id), all_reviews)
	return all_reviews


def display_review_partner(r, prof_id):
	display_attr = (prof_id == r.Review.prof_reviewed) and r.user or r.hero
	setattr(r, 'display', display_attr)


