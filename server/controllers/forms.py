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


from wtforms import TextField, TextAreaField, PasswordField, DecimalField
from wtforms import SelectField, BooleanField, RadioField, SelectMultipleField
from wtforms import IntegerField, HiddenField, FileField, DateField, validators
from wtforms.widgets import html_params, HTMLString, ListWidget, CheckboxInput
from wtforms.validators import Required
from cgi import escape
from flask.ext.wtf import Form
from server.models import *
from wtforms_components import DateTimeField, DateRange, Email
from werkzeug.datastructures import MultiDict


class SignupForm(Form):
	refid	= HiddenField('referred', [validators.Optional()])
	uname	= TextField('Name',  [validators.Optional(), validators.length(min=4, max=60)])		#what is max size in DB?
	email	= TextField('Email', [validators.Required(), validators.Email()])					#what is max size in DB?
	passw	= PasswordField('Password', [validators.Required()])
	#terms	= BooleanField('Terms of Service', [validators.Required()])


class ProSignupForm(Form):
	uname	= TextField('Name',  [validators.Optional(), validators.length(min=4, max=60)])		#what is max size in DB?
	passw	= PasswordField('Password', [validators.Required()])
	#terms	= BooleanField('Terms of Service', [validators.Required()])

	pro_name	= TextField('Business Name',	[validators.Optional(), validators.length(min=4, max=120)])
	pro_addr	= TextField('Business Address',	[validators.Required()])
	pro_phone	= TextField('Business Phone',	[validators.Required()])
	pro_email	= TextField('Business Email',	[validators.Required(), validators.Email()])



class LoginForm(Form):
	email	= TextField('Email', [validators.Required(), validators.Email()])
	passw	= PasswordField('Password', [validators.Required()])


class NewTrustedEntityForm(Form):
	name	= TextField('Name',		[validators.Required(), validators.length(min=4)])
	addr	= TextField('Address',	[validators.Optional()])
	site	= TextField('Website',	[validators.Optional()])
	phone	= TextField('Phone',	[validators.Optional()])
	email	= TextField('Email',	[validators.Optional(), validators.Email()])


class ProjectForm(Form):
	proj_id		= HiddenField('id')
	proj_name	= TextField('Name', [validators.Required(), validators.length(min=1, max=40)])
	proj_addr	= TextField('Address', [validators.Required(), validators.length(min=0, max=128)])
	proj_desc	= TextAreaField('Project Description', [validators.Required(), validators.length(min=0, max=5000)])
	#proj_min	= IntegerField('Minimum')
	proj_max	= IntegerField('Budget', [validators.Required()])
	proj_timeline	= TextField('Timeline', [validators.Required()])
	proj_contact	= TextField('Contact', [validators.Required()])


class ReferralForm(Form):
	bid = HiddenField('bid',	[validators.Required(), validators.length(min=30, max=40)])
	rid	= HiddenField('rid',	[validators.Optional(), validators.length(min=30, max=40)])

	content	= TextAreaField('ref',	[validators.Required(), validators.length(min=20, max=200)])
	context	= TextField('context',	[validators.Optional(), validators.length(min=0, max=120)])
	trusted	= TextField('Trusted',	[validators.Optional(), validators.length(min=4, max=100)])


class InviteForm(Form):
	invite_userid = HiddenField('userid',   [validators.Required(), validators.length(min=30, max=40)])
	invite_emails = TextField('Emails', [validators.Required(), validators.length(min=1, max=400)])
	invite_personalized = TextField('codeid', [validators.Optional(), validators.length(min=5, max=40)])


class GiftForm(Form):
	# names below (LHS) are used as the HTML element name.
	gift_name	= TextField('Name',	[validators.Required(), validators.length(min=2, max=128)])
	gift_addr	= TextField('Address', [validators.Optional(), validators.length(min=4, max=128)])
	gift_mail	= TextField('Email', [validators.Optional(), validators.Email(message=u'Invalid email address'), validators.length(min=6, max=50)])
	gift_cell	= TextField('Phone', [validators.Optional(), validators.length(min=7, max=15)])

	gift_from	= TextField('Name',	[validators.Required(), validators.length(min=2, max=128)])
	gift_note	= TextField('Note',	[validators.Optional(), validators.length(min=1, max=256)])
	gift_cost	= IntegerField('Cost', [validators.Required(), validators.length(min=4, max=120)])
	gift_value	= IntegerField('Value', [validators.Required(), validators.length(min=4, max=120)])



class SearchForm(Form):
	keywords_field = TextField('keywords-field')
	location_field = TextField('location-field')
#	industry_field = SelectField('Industry', coerce=str, choices=(Industry.enumInd))
	rate_from_field = IntegerField('rate-from')
	rate_to_field   = IntegerField('rate-to')


class SettingsForm(Form):
	name	= TextField('Name', [validators.Required()])
	email	= TextField('Email', [validators.Required()])
	update_password =	PasswordField('Password')
	verify_password	=	PasswordField('Password', [validators.EqualTo('update_password', 'Passwords must match')])
	current_password =	PasswordField('Password', [validators.Required()])


class RecoverPasswordForm(Form):
    email = TextField('Email', [validators.Required(), validators.Email()])


class NewPasswordForm(Form):
    rec_input_newpass = PasswordField('Password', [validators.Required()])



class ReviewForm(Form):
	review_id	 = HiddenField("id",	[validators.Required(), validators.length(min=1, max=40)])
	input_review = TextAreaField('Review') #,      [validators.length(min=0, max=5000)])
#	score_comm = SelectField('Communication', coerce=str, default=0, choices=(Review.enumRating))
#	score_time = SelectField('Promptness', coerce=str, default=0, choices=(Review.enumRating))


def checkfile(form,field):
	if field.data:
		filename=field.data.lower()
		ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
		if not ('.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS):
			raise ValidationError('Wrong Filetype, you can upload only png,jpg,jpeg,gif files')
		else:
			raise ValidationError('field not Present') # I added this justfor some debugging.



