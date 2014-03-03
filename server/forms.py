from wtforms import TextField, TextAreaField, PasswordField
from wtforms import SelectField, BooleanField, RadioField, FileField, HiddenField
from wtforms import IntegerField, validators
from wtforms.validators import Required
from flask.ext.wtf import Form
from server.infrastructure.models import Industry, Review





class RequiredIf(Required):
	# Validator which makes a field required conditionally on another field
	# http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms

	def __init__(self, other_field_name, *args, **kwargs):
		self.other_field_name = other_field_name
		super(RequiredIf, self).__init__(*args, **kwargs)

	def __call__(self, form, field):
		# check if this field is valid... 

		# get field from 'other_field_name', ensure it exists in the form
		other_field = form._fields.get(self.other_field_name)
		if other_field is None:
			raise Exception('no field named "%s" in form' % self.other_field_name)

		# if data exists, make this required by calling SuperObject. 
		if bool(other_field.data):
			super(RequiredIf, self).__call__(form, field)


NTS_times = [ ('00:00 AM', '00:00 AM'), ('00:30 AM', '00:30 AM'),
('01:00 AM', '01:00 AM'), ('01:30 AM', '01:30 AM'), ('02:00 AM', '02:00 AM'), 
('02:30 AM', '02:30 AM'), ('03:00 AM', '03:00 AM'), ('03:30 AM', '03:30 AM'), 
('04:00 AM', '04:00 AM'), ('04:30 AM', '04:30 AM'), ('05:00 AM', '05:00 AM'), 
('05:30 AM', '05:30 AM'), ('06:00 AM', '06:00 AM'), ('06:30 AM', '06:30 AM'), 
('07:00 AM', '07:00 AM'), ('07:30 AM', '07:30 AM'), ('08:00 AM', '08:00 AM'),
('08:30 AM', '08:30 AM'), ('09:00 AM', '09:00 AM'), ('09:30 AM', '09:30 AM'),
('10:00 AM', '10:00 AM'), ('10:30 AM', '10:30 AM'), ('11:00 AM', '11:00 AM'),
('11:30 AM', '11:30 AM'), ('12:00 PM', '12:00 PM'), ('12:30 PM', '12:30 PM'),
('13:00 PM', '13:00 PM'), ('13:30 PM', '13:30 PM'), ('14:00 PM', '14:00 PM'),
('14:30 PM', '14:30 PM'), ('15:00 PM', '15:00 PM'), ('15:30 PM', '15:30 PM'),
('16:00 PM', '16:00 PM'), ('16:30 PM', '16:30 PM'), ('17:00 PM', '17:00 PM'),
('17:30 PM', '17:30 PM'), ('18:00 PM', '18:00 PM'), ('18:30 PM', '18:30 PM'),
('19:00 PM', '19:00 PM'), ('19:30 PM', '19:30 PM'), ('20:00 PM', '20:00 PM'),
('20:30 PM', '20:30 PM'), ('21:00 PM', '21:00 PM'), ('21:30 PM', '21:30 PM'),
('22:00 PM', '22:00 PM'), ('22:30 PM', '22:30 PM'), ('23:00 PM', '23:00 PM'),
('23:30 PM', '23:30 PM')]


class NewAccountForm(Form):
	#names below (LHS) match what's on the HTML page.  
	input_signup_name   = TextField('Name',  [validators.Required(), validators.length(min=4, max=120)])
	input_signup_email  = TextField('Email', [validators.Required(), validators.Email(message=u'Invalid email address'), validators.length(min=6, max=50)])
	input_signup_password = PasswordField('Password', [validators.Required(), validators.EqualTo('input_signup_confirm', message='Passwords must match')])
	input_signup_confirm  = PasswordField('Repeat Password')
	accept_tos = BooleanField('TOS', [validators.Required()])

class LoginForm(Form):
	input_login_email    = TextField('Email', [validators.Required(), validators.Email()])
	input_login_password = PasswordField('Password', [validators.Required()])


class ProfileForm(Form):
	edit_name     = TextField('Name',     [validators.Required(), validators.length(min=1, max=40)])
	edit_headline = TextField('Headline') # [validators.Required(), validators.length(min=4, max=40)])
	edit_rate     = TextField('Rate' ) # [validators.Required(), validators.NumberRange(min=0, max=100000)])
	edit_location = TextField('Location')
	edit_industry = SelectField('Industry', coerce=str, choices=(Industry.enumInd))
	edit_url      = TextField('Website', [validators.URL(require_tld=True), validators.length(min=10, max=40)])
	edit_bio      = TextAreaField('Bio', [validators.length(min=0, max=5000)])
	edit_photo	  = FileField('Photo') #, [validators=[checkfile]])


class NTSForm(Form):
	hero                = HiddenField("Hero",	[validators.Required(), validators.length(min=1, max=40)])
	newslot_price       = TextField('Rate',		[validators.Required(), validators.NumberRange(min=0, max=None)])
	newslot_location    = TextField('Location', [validators.Required(), validators.length(min=1)])
	newslot_description = TextAreaField('Description') #,  [validators.length(min=6, max=40)])
	datepicker  = TextField('start-date')	#cannot be earlier than today
	datepicker1 = TextField('end-date')
	newslot_starttime   = SelectField('st', coerce=str, choices=NTS_times)
	newslot_endtime     = SelectField('et', coerce=str, choices=NTS_times)


class SearchForm(Form):
	keywords_field = TextField('keywords-field')
	location_field = TextField('location-field')
	industry_field = SelectField('Industry', coerce=str, choices=(Industry.enumInd))
	rate_from_field = IntegerField('rate-from')
	rate_to_field   = IntegerField('rate-to')


class SettingsForm(Form):
	oauth_stripe    = TextField('Stripe')
	set_input_email = TextField('Email', [validators.Email(), validators.Required()])
	set_input_curpass = PasswordField('Password', [RequiredIf('set_input_newpass')])
	set_input_newpass = PasswordField('Password')
	set_input_verpass = PasswordField('Password', [validators.EqualTo('set_input_newpass', 'Passwords must match')])


class RecoverPasswordForm(Form):
    rec_input_email = TextField('Email', [validators.Required(), validators.Email()])


class NewPasswordForm(Form):
    rec_input_newpass = PasswordField('Password', [validators.Required()])


class ProposalActionForm(Form):
	proposal_id   = TextField('id', [validators.Required()])
	proposal_stat = TextField('status', [validators.Required()])


class ReviewForm(Form):
	input_review = TextAreaField('Review') #,      [validators.length(min=0, max=5000)])
	input_rating = RadioField('Rating', coerce=str, choices=(Review.enumRating))


def checkfile(form,field):
	if field.data:
		filename=field.data.lower()
		ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
		if not ('.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS):
			raise ValidationError('Wrong Filetype, you can upload only png,jpg,jpeg,gif files')
		else:
			raise ValidationError('field not Present') # I added this justfor some debugging.


#class StripePaymentForm(CardForm):
#	def __init__(self, *args, **kwargs):
#		super(StripePaymentForm, self).__init__(*args, **kwargs)
#		self.fields['card_cvv'].label = "Card CVC"
#		self.fields['card_cvv'].help_text = "Card Verification Code; see rear of card."
#		self.fields['card_expiry_month'].choices = [(1, 'Jan'), (2, 'Feb'), (3, 'March'), (4, 'April')] 

#	card_number = forms.CharField(required=False, max_length=20, widget=NoNameTextInput())
#	card_cvv = forms.CharField(required=False, max_length=4, ())
#	card_expiry_month = forms.SelectField(required=False, choices=MONTHS.iteritems())
#	card_expiry_year = forms.SelectField(required=False, choices=options.ZEBRA_CARD_YEARS_CHOICES)
#
