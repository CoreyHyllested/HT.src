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


from . import sc_tests
from flask import render_template, make_response, session, request, redirect
from server.infrastructure.srvc_database import db_session
from server.models	import *
from server.infrastructure.errors	import *
from server.infrastructure.tasks	import *
from server.controllers				import *
from datetime import datetime as dt, timedelta
import json, smtplib, urllib


