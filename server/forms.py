from wtforms import TextField, TextAreaField, PasswordField, DecimalField
from wtforms import SelectField, BooleanField, RadioField, FileField, HiddenField
from wtforms import IntegerField, validators
from wtforms.widgets import html_params, HTMLString
from cgi import escape
from wtforms.validators import Required
from flask.ext.wtf import Form
from server.infrastructure.models import Industry, Review




class SelectWithDisable(object):
    """
    Renders a select field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of 
    `(value, label, selected, disabled)`.
    """
    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = 'multiple'
        html = [u'<select %s>' % html_params(name=field.name, **kwargs)]
        for val, label, selected, disabled in field.iter_choices():
            html.append(self.render_option(val, label, selected, disabled))
        html.append(u'</select>')
        return HTMLString(u''.join(html))

    @classmethod
    def render_option(cls, value, label, selected, disabled):
        options = {'value': value}
        if selected:
            options['selected'] = u'selected'
        if disabled:
            options['disabled'] = u'disabled'
        return HTMLString(u'<option %s>%s</option>' % (html_params(**options), escape(unicode(label))))




class SelectFieldWithDisable(SelectField):
    widget = SelectWithDisable()

    def iter_choices(self):
        for value, label, selected, disabled in self.choices:
            yield (value, label, selected, disabled, self.coerce(value) == self.data)



class MyOption(object):
	def __call__(self, field, **kwargs):
		options = dict(kwargs, value=field._value())
		if field.checked:
			options['selected'] = True

		label = field.label.text
		render_params = (html_params(**options), escape(unicode(label)))
		return HTMLString(u'<option %s>%s</option>' % render_params)



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

States = [("AL","Alabama"),("AK","Alaska"),("AZ","Arizona"),("AR","Arkansas"),
("CA","California"),("CO","Colorado"),("CT","Connecticut"),("DE","Delaware"),
("DC","District of Columbia"),("FL","Florida"),("GA","Georgia"),("HI","Hawaii"),
("ID","Idaho"),("IL","Illinois"),("IN","Indiana"),("IA","Iowa"),("KS","Kansas"),
("KY","Kentucky"),("LA","Louisiana"),("ME","Maine"),("MD","Maryland"),("MA","Massachusetts"),
("MI","Michigan"),("MN","Minnesota"),("MS","Mississippi"),("MO","Missouri"),("MT","Montana"),
("NE","Nebraska"),("NV","Nevada"),("NH","New Hampshire"),("NJ","New Jersey"),
("NM","New Mexico"),("NY","New York"),("NC","North Carolina"),("ND","North Dakota"),
("OH","Ohio"),("OK","Oklahoma"),("OR","Oregon"),("PA","Pennsylvania"),
("RI","Rhode Island"),("SC","South Carolina"),("SD","South Dakota"),("TN","Tennessee"),
("TX","Texas"),("UT","Utah"),("VT","Vermont"),("VA","Virginia"),
("WA","Washington"),("WV","West Virginia"),("WI","Wisconsin"),("WY","Wyoming")]

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




class LessonForm(Form):

	duration = ['No Set Duration', '30 minutes', '45 minutes', '1 hour', '1 hour 30 minutes']
	duratime = [-1, 30, 45, 60, 90 ]
	enumDura = zip(duratime, duration)

	lessonTitle			= TextField('Lesson Title', None)
	lessonDescription	= TextAreaField('Lesson Description', None)
	lessonAddress1	= TextField('Address Line 1', None)
	lessonAddress2	= TextField('Address Line 1', None)
	lessonCity		= TextField('City',	None)
	lessonState		= SelectField('State', coerce=str, default='CA', choices=(States))
	lessonZip		= TextField('Zip', None)
	lessonCountry	= TextField('Country', None)
	lessonAddressDetails = TextField('Details', None)
	lessonRate		= IntegerField('Rate Amount', None, default=50)
	lessonRateUnit	= SelectField('Rate Unit', coerce=int, choices=[(0,'Per Hour'),(1,'Per Lesson')])
	lessonPlace		= RadioField('Lesson Location', coerce=int, default=0, choices=[(0,'Flexible - I will arrange with student'), (1,'Student\'s place'), (2, 'My Place: ')])
	lessonIndustry	= SelectField('Lesson Industry', coerce=str, default='Other', choices=(Industry.enumInd2))
	lessonDuration	= SelectField('Lesson Duration', coerce=int, default=0, choices=(enumDura))
	lessonAvail = RadioField('Availability', coerce=int, default=0, choices=[(0,'Same as availability set in my profile'), (1,'Specific times (not available yet)')])



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

	newslot_ccname		= TextField('ccname',		[validators.Optional(), validators.length(min=1)])
	newslot_ccnbr		= TextField('ccnbr',		[validators.Optional()])
	newslot_ccexp		= TextField('ccexp',		[validators.Optional()])
	newslot_cccvv		= TextField('cccvv',		[validators.Optional()])

#

class SearchForm(Form):
	keywords_field = TextField('keywords-field')
	location_field = TextField('location-field')
	industry_field = SelectField('Industry', coerce=str, choices=(Industry.enumInd))
	rate_from_field = IntegerField('rate-from')
	rate_to_field   = IntegerField('rate-to')


class SettingsForm(Form):
	oauth_stripe    = TextField('Stripe')
	set_input_email = TextField('Email', [validators.Email(), validators.Required()])
	set_input_email_pass = PasswordField('Password', [RequiredIf('set_input_email')])
	set_input_curpass = PasswordField('Password', [RequiredIf('set_input_newpass')])
	set_input_newpass = PasswordField('Password')
	set_input_verpass = PasswordField('Password', [validators.EqualTo('set_input_newpass', 'Passwords must match')])


class RecoverPasswordForm(Form):
    rec_input_email = TextField('Email', [validators.Required(), validators.Email()])


class NewPasswordForm(Form):
    rec_input_newpass = PasswordField('Password', [validators.Required()])


class ProposalActionForm(Form):
	proposal_id   = TextField('id', [validators.Required()])
	proposal_stat = TextField('status')
	proposal_challenge = TextField('ch', [validators.Required()])


class ReviewForm(Form):
	review_id	 = HiddenField("id",	[validators.Required(), validators.length(min=1, max=40)])
	input_review = TextAreaField('Review') #,      [validators.length(min=0, max=5000)])
	input_rating = SelectField('Industry', coerce=str, default=0, choices=(Review.enumRating))
	score_comm = SelectField('Communication', coerce=str, default=0, choices=(Review.enumRating))
	score_time = SelectField('Promptness', coerce=str, default=0, choices=(Review.enumRating))


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
