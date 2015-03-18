from wtforms import TextField, TextAreaField, PasswordField, DecimalField
from wtforms import SelectField, BooleanField, RadioField, FileField, HiddenField, SelectMultipleField, DateField
from wtforms import IntegerField, validators
from wtforms.widgets import html_params, HTMLString, ListWidget, CheckboxInput
from cgi import escape
from wtforms.validators import Required
from flask.ext.wtf import Form
from server.models import *
from wtforms_components import DateTimeField, DateRange, Email
from werkzeug.datastructures import MultiDict


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




class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


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


NTS_times2 = [ 
('07:00', '7:00 AM'), ('07:30', '7:30 AM'), 
('08:00', '8:00 AM'), ('08:30', '8:30 AM'), 
('09:00', '9:00 AM'), ('09:30', '9:30 AM'),
('10:00', '10:00 AM'), ('10:30', '10:30 AM'), 
('11:00', '11:00 AM'), ('11:30', '11:30 AM'), 
('12:00', '12:00 PM'), ('12:30', '12:30 PM'),
('13:00', '1:00 PM'), ('13:30', '1:30 PM'), 
('14:00', '2:00 PM'), ('14:30', '2:30 PM'), 
('15:00', '3:00 PM'), ('15:30', '3:30 PM'),
('16:00', '4:00 PM'), ('16:30', '4:30 PM'), 
('17:00', '5:00 PM'), ('17:30', '5:30 PM'), 
('18:00', '6:00 PM'), ('18:30', '6:30 PM'),
('19:00', '7:00 PM'), ('19:30', '7:30 PM'), 
('20:00', '8:00 PM'), ('20:30', '8:30 PM'), 
('21:00', '9:00 PM'), ('21:30', '9:30 PM'),
]

NTS_times = [ 
('00:00', '12:00 AM'), ('00:30', '12:30 AM'),
('01:00', '1:00 AM'), ('01:30', '1:30 AM'), ('02:00', '2:00 AM'), 
('02:30', '2:30 AM'), ('03:00', '3:00 AM'), ('03:30', '3:30 AM'), 
('04:00', '4:00 AM'), ('04:30', '4:30 AM'), ('05:00', '5:00 AM'), 
('05:30', '5:30 AM'), ('06:00', '6:00 AM'), ('06:30', '6:30 AM'), 
('07:00', '7:00 AM'), ('07:30', '7:30 AM'), ('08:00', '8:00 AM'),
('08:30', '8:30 AM'), ('09:00', '9:00 AM'), ('09:30', '9:30 AM'),
('10:00', '10:00 AM'), ('10:30', '10:30 AM'), ('11:00', '11:00 AM'),
('11:30', '11:30 AM'), ('12:00', '12:00 PM'), ('12:30', '12:30 PM'),
('13:00', '1:00 PM'), ('13:30', '1:30 PM'), ('14:00', '2:00 PM'),
('14:30', '2:30 PM'), ('15:00', '3:00 PM'), ('15:30', '3:30 PM'),
('16:00', '4:00 PM'), ('16:30', '4:30 PM'), ('17:00', '5:00 PM'),
('17:30', '5:30 PM'), ('18:00', '6:00 PM'), ('18:30', '6:30 PM'),
('19:00', '7:00 PM'), ('19:30', '7:30 PM'), ('20:00', '8:00 PM'),
('20:30', '8:30 PM'), ('21:00', '9:00 PM'), ('21:30', '9:30 PM'),
('22:00', '10:00 PM'), ('22:30', '10:30 PM'), ('23:00', '11:00 PM'),
('23:30', '11:30 PM')]

NTS_times_start = NTS_times2[:]
NTS_times_end = NTS_times2[:]

NTS_times_start.insert(0, ('', 'Start Time'))
NTS_times_end.insert(0, ('', 'End Time'))

avail_times = [ ('00:00:00', '12:00 AM'), ('00:30:00', '12:30 AM'),
('01:00:00', '1:00 AM'), ('01:30:00', '1:30 AM'), ('02:00:00', '2:00 AM'), 
('02:30:00', '2:30 AM'), ('03:00:00', '3:00 AM'), ('03:30:00', '3:30 AM'), 
('04:00:00', '4:00 AM'), ('04:30:00', '4:30 AM'), ('05:00:00', '5:00 AM'), 
('05:30:00', '5:30 AM'), ('06:00:00', '6:00 AM'), ('06:30:00', '6:30 AM'), 
('07:00:00', '7:00 AM'), ('07:30:00', '7:30 AM'), ('08:00:00', '8:00 AM'),
('08:30:00', '8:30 AM'), ('09:00:00', '9:00 AM'), ('09:30:00', '9:30 AM'),
('10:00:00', '10:00 AM'), ('10:30:00', '10:30 AM'), ('11:00:00', '11:00 AM'),
('11:30:00', '11:30 AM'), ('12:00:00', '12:00 PM'), ('12:30:00', '12:30 PM'),
('13:00:00', '1:00 PM'), ('13:30:00', '1:30 PM'), ('14:00:00', '2:00 PM'),
('14:30:00', '2:30 PM'), ('15:00:00', '3:00 PM'), ('15:30:00', '3:30 PM'),
('16:00:00', '4:00 PM'), ('16:30:00', '4:30 PM'), ('17:00:00', '5:00 PM'),
('17:30:00', '5:30 PM'), ('18:00:00', '6:00 PM'), ('18:30:00', '6:30 PM'),
('19:00:00', '7:00 PM'), ('19:30:00', '7:30 PM'), ('20:00:00', '8:00 PM'),
('20:30:00', '8:30 PM'), ('21:00:00', '9:00 PM'), ('21:30:00', '9:30 PM'),
('22:00:00', '10:00 PM'), ('22:30:00', '10:30 PM'), ('23:00:00', '11:00 PM'),
('23:30:00', '11:30 PM')]

avail_times_start = NTS_times[:]
avail_times_end = NTS_times[:]

# avail_times_start.insert(0, ('', 'Start Time'))
# avail_times_end.insert(0, ('', 'End Time'))

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

Days = [
	(0,'Sunday'), 
	(1,'Monday'),
	(2,'Tuesday'),	
	(3,'Wednesday'),
	(4,'Thursday'),
	(5,'Friday'),
	(6,'Saturday')
]

Location = [('location_ip', "Your Location"), ('location_berkeley', "Berkeley, CA"), ('location_other', "Other")]


class NewAccountForm(Form):
	# names below (LHS) are used as the HTML element name.
	input_signup_name   = TextField('Name',  [validators.Required(), validators.length(min=4, max=120)])
	#input_signup_location = SelectField("Location", coerce=str, choices=(Location))
	input_signup_email  = TextField('Email', [validators.Required(), validators.Email(message=u'Invalid email address'), validators.length(min=6, max=50)])
	input_signup_password = PasswordField('Password', [validators.Required(), validators.EqualTo('input_signup_confirm', message='Passwords must match')])
	input_signup_confirm  = PasswordField('Confirm Password')
	accept_tos = BooleanField('TOS', [validators.Required()])

class SignupForm(Form):
	uname	= TextField('Name',  [validators.Optional(), validators.length(min=4, max=60)])
	email	= TextField('Email', [validators.Required(), validators.Email()])
	passw	= PasswordField('Password', [validators.Required()])

class LoginForm(Form):
	email	= TextField('Email', [validators.Required(), validators.Email()])
	passw	= PasswordField('Password', [validators.Required()])




class LessonForm(Form):

	Durations = [ (30, '30 minutes'), (60, '1 hour'), (90, '1 hour 30 minutes'), (120, '2 hours'), (150, '2 hours 30 minutes'), (180, '3 hours'), (210, '3 hours 30 minutes'), (240, '4 hours'), (270, '4 hours 30 minutes'), (300, '5 hours'), (330, '5 hours 30 minutes'), (360, '6 hours') ]

	lessonTitle			= TextField('Lesson Title', [validators.Required(), validators.length(min=1, max=120)])
	lessonDescription	= TextAreaField('Lesson Description', [validators.Required(), validators.length(min=1, max=100000)])
	lessonAddress1	= TextField('Address Line 1', None)
	lessonAddress2	= TextField('Address Line 1', None)
	lessonCity		= TextField('City',	None)
	lessonState		= SelectField('State', coerce=str, default='CA', choices=(States))
	lessonZip		= TextField('Zip', None)
	lessonCountry	= TextField('Country', None)
	lessonAddressDetails = TextField('Details', None)
	lessonRate		= IntegerField('Rate Amount', None, default=100)
	lessonRateUnit	= SelectField('Rate Unit', coerce=int, choices=[(0,'Per Hour'),(1,'Per Lesson')])
	lessonPlace		= RadioField('Lesson Location', coerce=int, default=0, choices=[(0,'Flexible location'), (2, 'My Place: ')])
	lessonIndustry	= SelectField('Lesson Industry', coerce=str, default='Other', choices=(Industry.enumInd2))
	lessonDuration	= SelectField('Lesson Duration', coerce=int, default=60, choices=(Durations))
	lessonMaterialsProvided	= TextAreaField('Materials Provided', [validators.length(min=0, max=100000)])
	lessonMaterialsNeeded	= TextAreaField('Materials Needed', [validators.length(min=0, max=100000)])
	lessonAvail = RadioField('Availability', coerce=int, default=0, choices=[(0,'Same as availability set in my profile'), (1,'Specific times (not available yet)')])
	lessonMakeLive = BooleanField('Make this lesson live and public!', None)


class ProjectForm(Form):
	proj_id		= HiddenField('id')
	proj_name	= TextField('Name', [validators.Required(), validators.length(min=1, max=40)])
	proj_addr	= TextField('Address', [validators.Required(), validators.length(min=0, max=128)])
	proj_desc	= TextAreaField('Project Description', [validators.Required(), validators.length(min=0, max=5000)])
	#proj_min	= IntegerField('Minimum')
	proj_max	= IntegerField('Budget', [validators.Required()])
	proj_timeline	= TextField('Timeline', [validators.Required()])
	proj_contact	= TextField('Contact', [validators.Required()])

	#avail_day = SelectField('Day', coerce=int, choices=Days)
	#avail_time = SelectField('Start time', coerce=str, choices=NTS_times_start)



class InviteForm(Form):
	invite_userid = HiddenField('userid',   [validators.Required(), validators.length(min=30, max=40)])
	invite_emails = TextField('Emails', [validators.Required(), validators.length(min=1, max=400)])
	invite_personalized = TextField('codeid', [validators.Optional(), validators.length(min=5, max=40)])



class ProfileForm(Form):
	edit_name     = TextField('Name', [validators.Required(), validators.length(min=1, max=40)])
	edit_location = TextField('Location')
	edit_bio      = TextAreaField('Bio', [validators.length(min=0, max=5000)])
	edit_photo	  = FileField('Photo') #, [validators=[checkfile]])
	edit_headline = TextField('Headline') # [validators.Required(), validators.length(min=4, max=40)])
	edit_rate     = TextField('Rate' ) # [validators.Required(), validators.NumberRange(min=0, max=100000)])
	edit_industry = SelectField('Category', coerce=str, choices=(Industry.enumInd2))
	edit_url      = TextField('Website') #, [validators.URL(require_tld=True), validators.length(min=10, max=40)])
	edit_oauth_stripe = TextField('Stripe')
	edit_availability = SelectField('Availability', coerce=int, choices=[(1,'Flexible - will arrange with students'),(2,'Specific (select times below)')])
	edit_mentor_live = BooleanField('Make my mentor profile live!', None)
	edit_mentor_tos = BooleanField('I have read and understand Insprite\'s <a href="/tos" target="_new">Terms of Service</a>', [validators.Required()])
	edit_industry = SelectField('Category', coerce=str, choices=(Industry.enumInd))

	edit_avail_day_sun = BooleanField('Sunday')
	edit_avail_day_mon = BooleanField('Monday')
	edit_avail_day_tue = BooleanField('Tuesday')
	edit_avail_day_wed = BooleanField('Wednesday')
	edit_avail_day_thu = BooleanField('Thursday')
	edit_avail_day_fri = BooleanField('Friday')
	edit_avail_day_sat = BooleanField('Saturday')

	edit_avail_time_mon_start	= SelectField('Mon Start', coerce=str, choices=NTS_times_start)
	edit_avail_time_mon_finish		= SelectField('Mon End', coerce=str, choices=NTS_times_end)
	edit_avail_time_tue_start	= SelectField('Tue Start', coerce=str, choices=NTS_times_start)
	edit_avail_time_tue_finish		= SelectField('Tue End', coerce=str, choices=NTS_times_end)
	edit_avail_time_wed_start	= SelectField('Wed Start', coerce=str, choices=NTS_times_start)
	edit_avail_time_wed_finish		= SelectField('Wed End', coerce=str, choices=NTS_times_end)
	edit_avail_time_thu_start	= SelectField('Thu Start', coerce=str, choices=NTS_times_start)
	edit_avail_time_thu_finish		= SelectField('Thu End', coerce=str, choices=NTS_times_end)
	edit_avail_time_fri_start	= SelectField('Fri Start', coerce=str, choices=NTS_times_start)
	edit_avail_time_fri_finish		= SelectField('Fri End', coerce=str, choices=NTS_times_end)
	edit_avail_time_sat_start	= SelectField('Sat Start', coerce=str, choices=NTS_times_start)
	edit_avail_time_sat_finish		= SelectField('Sat End', coerce=str, choices=NTS_times_end)
	edit_avail_time_sun_start	= SelectField('Sun Start', coerce=str, choices=NTS_times_start)
	edit_avail_time_sun_finish		= SelectField('Sun End', coerce=str, choices=NTS_times_end)



class ProposalForm(Form):
	prop_mentor      = HiddenField("Mentor",	[validators.Required(), validators.length(min=1, max=40)])
	prop_price       = TextField('Rate',		[validators.Required(), validators.NumberRange(min=0, max=None)])
	prop_location    = TextField('Location')
	prop_lesson      = SelectField('Lesson', coerce=str)
	prop_description = TextAreaField('Description') #,  [validators.length(min=6, max=40)])
	prop_starttime   = SelectField('Choose Start Time', coerce=str, choices=NTS_times_start)
	prop_finishtime     = SelectField('Choose End Time', coerce=str, choices=NTS_times_end)
	prop_date 		 = DateField('Date')

	# prop_date = DateTimeField('Date', validators=[DateRange(min=datetime(2000, 1, 1), max=datetime(2000, 10, 10))])

class SearchForm(Form):
	keywords_field = TextField('keywords-field')
	location_field = TextField('location-field')
	industry_field = SelectField('Industry', coerce=str, choices=(Industry.enumInd))
	rate_from_field = IntegerField('rate-from')
	rate_to_field   = IntegerField('rate-to')


class SettingsForm(Form):
	set_input_name	= TextField('Name', [validators.Required()])
	set_input_email = TextField('Email', [validators.Required()])	
	set_input_newpass = PasswordField('Password')
	set_input_verpass = PasswordField('Password', [validators.EqualTo('set_input_newpass', 'Passwords must match')])
	set_input_curpass = PasswordField('Password', [validators.Required()])


class RecoverPasswordForm(Form):
    email = TextField('Email', [validators.Required(), validators.Email()])


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


# class NTSForm(Form):
# 	mentor                = HiddenField("Mentor",	[validators.Required(), validators.length(min=1, max=40)])
# 	newslot_price       = TextField('Rate',		[validators.Required(), validators.NumberRange(min=0, max=None)])
# 	newslot_location    = TextField('Location', [validators.Required(), validators.length(min=1)])
# 	newslot_description = TextAreaField('Description') #,  [validators.length(min=6, max=40)])
# 	datepicker  = TextField('start-date')	#cannot be earlier than today
# 	datepicker1 = TextField('end-date')
# 	newslot_starttime   = SelectField('st', coerce=str, choices=NTS_times)
# 	newslot_endtime     = SelectField('et', coerce=str, choices=NTS_times)

# 	newslot_ccname		= TextField('ccname',		[validators.Optional(), validators.length(min=1)])
# 	newslot_ccnbr		= TextField('ccnbr',		[validators.Optional()])
# 	newslot_ccexp		= TextField('ccexp',		[validators.Optional()])
# 	newslot_cccvv		= TextField('cccvv',		[validators.Optional()])

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
