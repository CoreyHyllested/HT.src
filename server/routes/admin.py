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


from . import sc_admin
from flask import render_template
from .helpers import *
from server.controllers import *
from server.sc_utils import *


@sc_admin.route('/admin', methods=['GET', 'POST'])
def render_admin_dashboard():
	bp = Profile.get_by_uid(session['uid'])
	return make_response(render_template('dashboard-admin.html', bp=bp))
