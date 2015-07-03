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


from server.models import *
from server.controller.images import *
from datetime import datetime as dt


def ht_validate_profile(bp, form, form_page):
	errors = {}
	print "ht_validate_page: validating page: ", form_page

	if (form_page == "general" or form_page == "full"):
		prof_name = request.values.get("edit_name")
		prof_location = request.values.get("edit_location")
		prof_bio = request.values.get("edit_bio")

		if (len(prof_name) == 0):
			errors["edit_name"] = "Profile name is required." 
		elif (len(prof_name) > 40):
			errors["edit_name"] = "This must be less than 40 characters."

	if (form_page == "profile_photo" or form_page == "full"):

		file = request.files[form.edit_photo.name]
		print "ht_validate_page: uploaded filename is ", file.filename
		if (file):
			if allowed_file(file.filename):
				print "That photo works."
			else:
				print "File was not an image."
				errors["edit_photo"] = "Please only upload jpg, gif, or png files." 
		else :
			print "No photo uploaded."
			if (form_page == "full" and bp.prof_img == "no_pic_big.svg"):
				errors["edit_photo"] = "All mentors must upload a profile photo." 		

	if (form_page == "details" or form_page == "full"):
		prof_headline = request.values.get("edit_headline")
		# prof_url = request.values.get("edit_url")

		if (len(prof_headline) == 0):
			errors["edit_headline"] = "We'd really love for you to come up with something here." 
		elif (len(prof_headline) > 40):
			errors["edit_headline"] = "This must be less than 40 characters."

	if (form_page == "schedule" or form_page == "full"):
		# once date/time form elements are in, check if:
		# 1. specific was selected without specifying times
		# 2. day was selected without specifying time
		# 3. end time was before start time on any day

		print "validate_profile: validating schedule page"

		new_avail = request.values.get("edit_availability")
		print "validate_profile: new_avail: ", new_avail
		print "validate_profile: edit_avail_day_tue: ", request.values.get("edit_avail_day_tue")

		if (new_avail == "2"):
			days = []
			if (request.values.get("edit_avail_day_sun") == 'y'): days.append("sun")
			if (request.values.get("edit_avail_day_mon") == 'y'): days.append("mon")
			if (request.values.get("edit_avail_day_tue") == 'y'): days.append("tue")
			if (request.values.get("edit_avail_day_wed") == 'y'): days.append("wed")
			if (request.values.get("edit_avail_day_thu") == 'y'): days.append("thu")
			if (request.values.get("edit_avail_day_fri") == 'y'): days.append("fri")
			if (request.values.get("edit_avail_day_sat") == 'y'): days.append("sat")

			print "validate_profile: days: ", pp(days)

			for day in days:
				print "validate_profile: day is: ", day
				start = eval("form.edit_avail_time_"+day+"_start.data")
				finish = eval("form.edit_avail_time_"+day+"_finish.data")
				
				if (start == '' or finish == ''):
					errors[day] = "Please select both a start and end time."
				else:
					try: 
						starttime = dt.strptime(start, '%H:%M')
						finishtime = dt.strptime(finish, '%H:%M')
						if (finishtime <= starttime):
							errors[day] = "End time must be later than start time."
					except:
						errors[day] = "Hmm... unknown error here."

			if (len(days) == 0):
				errors["edit_availability"] = "Please select the specific days and times you will be available"


	if (form_page == "payment" or form_page == "full"):
		#PROF_RATE was removed
		#prof_rate = request.values.get("edit_rate")	
		oauth_stripe = request.values.get("edit_oauth_stripe")

		#print "validate_profile: prof rate is: ", prof_rate

		#try:
		#	prof_rate = int(prof_rate)
		#	if (prof_rate > 10000):
		#		errors["edit_rate"] = "Let's keep it below $10,000 for now."
		#except TypeError:
		#	errors["edit_rate"] = "Please keep it to a whole dollar amount (or zero)."

		if (oauth_stripe == ''):
			errors["edit_oauth_stripe"] = "Stripe activation is required to become a mentor."

	if (form_page == "full"):		
		tos = request.values.get("edit_mentor_tos")
		print "tos is ", tos
		if (tos != 'y'):
			errors["edit_mentor_tos"] = "You'll need to agree to the terms of service first."


	if (len(errors) == 0):
		print "validate_profile: form is valid."
		valid = True
	else:
		print "validate_profile: errors: ", pp(errors)
		valid = False
	return valid, errors



def ht_update_profile(ba, bp, form, form_page):
	print 'ht_update_profile:', bp.prof_id
	print 'ht_update_profile: form_page: ', form_page
	if (form_page == "full"):
		print 'ht_update_profile: save all elements'
	else:
		print 'ht_update_profile: save only elements from page: ', form_page
	for key in request.values:
		print '\t', key, request.values.get(key)
	update = False
	
	if (form_page == 'general' or form_page == 'full'):
		bp.prof_name = form.edit_name.data
		bp.location = form.edit_location.data 			
		bp.prof_bio  = form.edit_bio.data
		return True

	if (form_page == 'details' or form_page == 'full'):	
		bp.headline = form.edit_headline.data 			
		bp.prof_url  = form.edit_url.data
		return True

	# check for photo, name should be PHOTO_HASH.VER[#].SIZE[SMLX]
	if (form_page == 'profile_photo' or form_page == 'full'):
		file = request.files[form.edit_photo.name]
		print "ht_validate_page: uploaded filename is ", file.filename
		if (file and allowed_file(file.filename)):
			image_data = file.read()
			print "api_update_profile: image was uploaded"
			destination_filename = str(hashlib.sha1(image_data).hexdigest()) + '.jpg'
			trace (destination_filename + ", sz = " + str(len(image_data)))

			print 'api_update_profile: s3'
			conn = boto.connect_s3(sc_server.config["S3_KEY"], sc_server.config["S3_SECRET"]) 
			b = conn.get_bucket(sc_server.config["S3_BUCKET"])
			sml = b.new_key(sc_server.config["S3_DIRECTORY"] + destination_filename)
			sml.set_contents_from_file(StringIO(image_data))
			imglink   = 'https://s3-us-west-1.amazonaws.com/htfileupload/htfileupload/'+destination_filename
			bp.prof_img = destination_filename

		# if URL is set, ensure 'http(s)://' is part of it
		if (bp.prof_url):
			if (bp.prof_url[:8] != "https://"):
				if (bp.prof_url[:7] != "http://"):
					bp.prof_url = "http://" + bp.prof_url;
		return True

