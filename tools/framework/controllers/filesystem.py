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

import sys, os
from pprint import pprint as pp


def safe_mkdir_local(path):
	directory = os.getcwd() + path
	safe_mkdir(directory)


def safe_mkdir(directory):
	if (os.path.exists(directory) == False):
		os.makedirs(directory)

