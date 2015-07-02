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

from flask import Blueprint
from flask import render_template, session, request
from pprint import pprint as pp
import uuid

sc_users = Blueprint('sc_users', __name__)
sc_ebody = Blueprint('sc_ebody', __name__)
sc_tests = Blueprint('sc_tests', __name__)
meta_routes = Blueprint('meta_routes', __name__)
api_routing = Blueprint('routing_api', __name__)
print 'loading', __name__

