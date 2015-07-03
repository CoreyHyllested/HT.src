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


from flask import render_template
from server import database
from server.models import *
from server.routes import api_routing as api 
from server.routes.helpers import *
from server.controllers import *



#@api.route('/review/request', methods=['POST'])
@sc_authenticated
def api_review_request():
	print 'api_review_request(): enter'
	email = request.values.get('invite_emails', None)
	resend = request.values.get('resend_emails', None)
	resp_code	= 200
	resp_mesg	= 'Created'
	fragment	= None

	try:
		# DOESN'T THROW ERRORS.
		brr = BusinessReference.get_by_email(session['pid'], email)
		if (brr is not None):
			resp_mesg	= 'Request exists.'

			if resend:
				brr.resend()
				database.session.add(brr)
				database.session.commit()
				sc_send_BR_email(session['pid'], email, brr)
			return make_response(jsonify(sc_msg=resp_mesg, brid=brr.br_uuid), resp_code)

		if (brr is None):
			brr = BusinessReference(session['uid'], session['pid'], email)
			database.session.add(brr)
			database.session.commit()
			fragment = render_template('fragment_request.html', brr=brr)
			sc_send_BR_email(session['pid'], email, brr)
	except Exception as e:
		database.session.rollback()
		print 'Uh oh fellas.', type(e), e
		resp_code = 400
		resp_mesg = 'An error occurred'

	# if email already exists... send back 200 (scroll-to and flash border?)
	return make_response(jsonify(sc_msg=resp_mesg, embed=fragment), resp_code)



@sc_authenticated
def api_review_create(review_id):
	msg = None
	uid = session['uid']
	bp = Profile.get_by_uid(session['uid'])

	review_form = ReviewForm(request.form)
	print review_form.review_id.data
	print review_form.input_review.data
	print review_form.input_rating.data  #score_meet.data
	print review_form.score_comm.data
	print review_form.score_time.data

	# check review for validity.
	if review_form.validate_on_submit():
		print 'ht_api_review_create() form is valid'
		try:
			# get review from database, modify and update review.
			review = Review.get_by_id(review_form.review_id.data)
			review.appt_score = int(review_form.input_rating.data)
			review.generalcomments = review_form.input_review.data
			review.score_attr_comm = int(review_form.score_comm.data)
			review.score_attr_time = int(review_form.score_time.data)
			review.set_state(REV_STATE_FINSHED)
			print 'ht_api_review_create() form is updated'

			database.session.add(review)
			database.session.commit()
			#log_uevent(uid, "posting " + str(review))

			print 'ht_api_review_create() data has been posted'
			profile_reviewed = Profile.get_by_prof_id(review.prof_reviewed)		# reviewed profile
			ht_post_review(review)

			# thank user for submitting review & making the world a better place
			return jsonify(usrmsg='Thanks for submitting review. It will be posted shortly'), 200
		except Exception as e:
			print "ht_api_review_create().  Exception...\n", type(e), e
			database.session.rollback()
			raise e
	elif request.method == 'POST':
		print "ht_api_review_create()  POST isn't valid " + str(review_form.errors)
		msg = {}
		for error in review_form.errors:
			if (error == 'input_rating'): key = "Overall Value option"
			elif (error == 'score_comm'): key = "Communication option"
			elif (error == 'score_time'):	key = "Promptness option"
			elif (error == 'input_review'):	key = "Your Experience"
			msg[key] = review_form.errors[error][0].decode().lower()
		return jsonify(usrmsg=msg), 400
	else:
		print "ht_api_review_create()  form wasn't posted"
		
	return make_response(render_template('review.html', title = '- Write Review', bp=bp, hero=profile_reviewed, form=review_form, usrmsg=msg))



#@insprite_views.route("/review/new/<review_id>", methods=['GET', 'POST'])
#@req_authentication
def render_review_meeting_page(review_id):
	"""renders review page.  Results posted to ht_api_review"""
	print 'render_review_meeting()\treview_id =', review_id
	# if review already exists, return a kind message.

	try:
		review = Review.get_by_id(review_id)
		review_days_left = review.time_until_review_disabled()
		if (review_days_left < 0):
			return jsonify(msg='Reviews are only available for 30 days after a meeting'), 400
		if (review.completed()):
			raise StateTransitionError(review.review_id, review.rev_status, review.rev_status, msg="Reviews cannot be modified once submitted")
			#return make_response(jsonify(msg='Reviews cannot be modified once submitted'), 400

		bp = Profile.get_by_uid(session['uid'])
		ba = Account.get_by_uid(bp.account)

		author = bp
		review.validate_author(author.prof_id)

		reviewed = Profile.get_by_prof_id(review.prof_reviewed)
		print 'render_review()\t, author =', author.prof_id, author.prof_name, ba.email
		print 'render_review()\t, review author =', review.prof_authored
		print 'render_review()\t, review revied =', review.prof_reviewed

		review_form = ReviewForm(request.form)
		review_form.review_id.data = str(review_id)
		return make_response(render_template('review.html', title = '- Write Review', bp=bp, hero=reviewed, form=review_form))

	except SanitizedException as se:
		print se
		database.session.rollback()
		return jsonify(usrmsg=se.sanitized_msg())
	except Exception as e:
		print type(e), e
		database.session.rollback()
		raise e
	except IndexError as ie:
		print 'trying to access, review, author or reviewer account and failed'
		database.session.rollback()
		raise ie




################################################################################
### API HELPER FUNCTIONS. ######################################################
################################################################################


def profile_update_reviews(profile):
	print 'profile_update_reviews, updating profile,', profile.prof_name, profile.prof_id, '...\n'

	try:
		all_visible_reviews = Review.query.filter_by(prof_reviewed = profile.prof_id).filter_by(rev_status = REV_STATE_VISIBLE).all()

		profile_rating = 0
		print '\t', 'total of', len(all_visible_reviews)
		for review in all_visible_reviews:
			profile_rating += review.appt_score
			print '\t', review, ' quality points = ', profile_rating

		profile.updated = dt.now()
		profile.reviews = len(all_visible_reviews)
		profile.rating  = float(profile_rating) / len(all_visible_reviews)

		print(profile.prof_id, "now has " + str(profile_rating) + " points, and " + str(len(all_visible_reviews)) + " for a rating of " + str(profile.rating)) #log_uevent
		database.session.add(profile)
		database.session.commit()
	except Exception as e:
		print 'updating profile,', profile.prof_id, '...\n', type(e), e
		database.session.rollback()
		raise e




def ht_post_review(review):
	""" Check if sibling-review is posted; if so make them both reviews visible. """
	meeting = Meeting.get_by_id(review.rev_appt)
	rev_sellr_id = meeting.review_sellr		# review mentor
	rev_buyer_id = meeting.review_buyer		# review mentee

	review_twin_id = (review.review_id == rev_sellr_id) and rev_buyer_id or rev_sellr_id
	review_twin = Review.get_by_id(review_twin_id)
	print 'ht_post_review(): ' + str(review.review_id) + '\treview_twin: ' + str(review_twin_id)
	if (review_twin is None): raise NoReviewFound(review_twin_id) 

	if (not review_twin.completed()):
		print 'ht_posting_review_update_proposal():  just this review is available.'
		return

	try:
		print 'ht_posting_review_update_proposal():  make both reviews live'
		review.set_state(REV_STATE_VISIBLE)
		review.updated = dt.utcnow()
		review_twin.set_state(REV_STATE_VISIBLE)
		review_twin.updated = dt.utcnow()

		print 'ht_posting_review_update_proposal():  commit to DB'
		database.session.add(review)
		database.session.add(review_twin)
	except Exception as e:
		print 'ht_posting_review_update_proposal(): ', type(e), e
		database.session.rollback()

	print 'ht_posting_review_update_proposal(): update profiles'
	profile_sellr = Profile.get_by_prof_id(review.prof_authored)		# authored profile
	profile_buyer = Profile.get_by_prof_id(review.prof_reviewed)		# reviewed profile
	print 'ht_posting_review_update_proposal(): profile', profile_sellr.prof_name
	print 'ht_posting_review_update_proposal(): profile', profile_buyer.prof_name
	profile_update_reviews(profile_sellr)
	profile_update_reviews(profile_buyer)





