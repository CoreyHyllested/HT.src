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


from server import sc_server
from server.models import *
from server.routes import api_routing as api
from server.routes import test_routes as test
from server.routes.helpers import *
from server.controllers import *



@api.route('/project/update', methods=['POST'])
@sc_authenticated
def api_update_project(usrmsg=None):
	# Process the edit profile form
	print "api_proj_update: start"

	uid = session['uid']
	bp = Profile.get_by_uid(uid)
	
	# validate all data manually. 
	form = ProjectForm(request.form)

	try:
		errors = "CAH, no errors"
		if form.validate_on_submit():
			print "api_proj_update: valid submit"

			if (True):
				project = None
				newproj = False
				print "api_proj_update: id = ", form.proj_id.data
				if form.proj_id is not 'new':
					# find project.
					project = Project.get_by_proj_id(form.proj_id.data)

				if (project == None):
					print "api_proj_update: create new project"
					project = Project(form.proj_name.data, uid)
					newproj = True;
					if (project == None):
						err_msg = 'Error: user(%s) gave us a bad ID(%s), BAIL!' % (uid, form.proj_name.data)
						raise err_msg

				print "api_proj_update: set details"
				project.proj_name	= form.proj_name.data
				project.proj_addr	= form.proj_addr.data
				project.proj_desc	= form.proj_desc.data
				project.proj_min	= 0	#hardcoding to zero
				project.proj_max	= form.proj_max.data	#rename_budget (budget_actual?)
				project.timeline 	= form.proj_timeline.data
				project.contact		= form.proj_contact.data
				project.updated		= datetime.utcnow()

				print "api_proj_update: add"
				database.session.add(project)
				database.session.commit()
				if (newproj): sc_email_newproject_created(bp, project)
				return jsonify(usrmsg="project updated", proj_id=project.proj_id), 200
			else:
				database.session.rollback()
				print "api_proj_update: update error"
				return jsonify(usrmsg="We messed something up, sorry", errors=form.errors), 500
		else:
			print 'api_proj_update: invalid POST', form.errors

		print "api_proj_update: invalid", 
		return jsonify(usrmsg='Sorry, some required info was missing or in an invalid format. Please check the form.', errors=form.errors), 500

	except AttributeError as ae:
		print "api_proj_update: exception", ae
		database.session.rollback()
		return jsonify(usrmsg='We messed something up, sorry'), 500
	except Exception as e:
		print type(e), e
		print "api_proj_update: exception", e
		database.session.rollback()
		return jsonify(usrmsg=e), 500

	print "api_update_profile: Something went wrong - Fell Through."
	print "here is the form object:"
	print str(form)

	print "api_proj_update: return"
	return jsonify(usrmsg="Something went wrong."), 500



@api.route('/project/edit', methods=['GET', 'POST'])
@api.route('/project/edit/<string:pid>', methods=['GET', 'POST'])
@sc_authenticated
def render_edit_project(pid=None):
	bp = Profile.get_by_uid(session['uid'])
	print "render_edit_project: profile[" + str(bp.prof_id) + "] project[" + str(pid) + "]"

	form = ProjectForm(request.form)
	project = Project.get_by_proj_id(pid, bp) # FEATURE: project should be _owned_ by bp (not checked right now)
	if (project):
		form.proj_id.data	= project.proj_id
		form.proj_name.data	= project.proj_name
		form.proj_addr.data = project.proj_addr
		form.proj_desc.data = project.proj_desc
		form.proj_max.data	= project.proj_max
		form.proj_timeline.data	= project.timeline
		form.proj_contact.data	= project.contact

#		print "render_edit_project: checking for scheduled time."
#		schedule_call = Availability.get_project_scheduled_time(project.proj_id)
#		if (schedule_call is not None):
#				print "render_edit_project: setting values to ", str(schedule_call.avail_weekday), str(schedule_call.avail_start), str(schedule_call.avail_start)[:-3]
#				form.avail_day.data  = schedule_call.avail_weekday
#				form.avail_time.data = str(schedule_call.avail_start)[:-3]
	else:
		# set proj_id to 'new'
		form.proj_id.data	= 'new'

	return make_response(render_template('edit_project.html', form=form, bp=bp))



@api.route('/project/schedule/<mode>/<string:pid>', methods=['GET', 'POST'])
@sc_authenticated
def api_project_schedule_consultation(mode, pid=None):
	bp = Profile.get_by_uid(session['uid'])
	try:
		project = Project.get_by_proj_id(pid, bp)
		if (project):
			session['message'] = 'A project specialist will contact you by ' + str(mode) + ' within 24 hours.'
	except Exception as e:
		print e
	return redirect('/dashboard')




