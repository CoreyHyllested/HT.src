from flask import render_template
from . import insprite_views



@insprite_views.app_errorhandler(404)
def page_not_found(e):
	print 'rendering 404'
	return render_template('404.html'), 404




@insprite_views.app_errorhandler(500)
def internal_server_error(e):
	print 'rendering 500'
	return render_template('500.html'), 500
