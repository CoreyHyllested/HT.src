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

import re
import json

def uri_strip_http(uri):
	if 'https://' in uri[0:8]:
		return uri[8:]
	if 'http://' in uri[0:7]:
		return uri[7:]


def url_clean(uri):
	uri = uri_strip_http(uri)
	uri = uri.rstrip('/ ')
	uri = re.sub('[/:]','_', uri)
	return uri


def webcache_url(URI):
	return 'https://webcache.googleusercontent.com/search?q=cache:' + uri_strip_http(URI)

