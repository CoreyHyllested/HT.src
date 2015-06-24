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
import urltools

def uri_strip_http(uri):
	if 'https://' in uri[0:8]:
		return uri[8:]
	if 'http://' in uri[0:7]:
		return uri[7:]
	return uri


def url_clean(uri):
	uri = uri_strip_http(uri)
	uri = uri.rstrip('/ ')
	uri = re.sub('[/: ]','_', uri)
	return uri


def webcache_url(URI):
	return 'https://webcache.googleusercontent.com/search?q=cache:' + uri_strip_http(URI)

def normalize_webaddr(uri):
	if (not uri): return None
	uri = urltools.normalize(uri.lower())
	uri = uri.replace('http://www.',	 'http://')
	uri = uri.replace('https://www.', 'http://')
	uri = remove_nonsense_hosts(uri)
	return uri



def remove_nonsense_locators(uri):
	strip = [ 'http://ferguson.com/branch/denver-co-plumbing/?CID=YPM_Ad___YPM___YELPAG__BRAF' ]
	return uri


def remove_nonsense_hosts(uri):
	dumb_hosts = [	'adzzup.com',
				'datasphere.com'
				'dnslink.com'
				'donotproxy.com',
				'google.com',
				'googlesyndication.com',
				'hobbylobby.com',
				'homeadvisor.com',
				'hostmonster.com',
				'hugedomains.com',
				'ibizlocal.net',
				'justgoodbusiness.biz',
				'secureserver.net',
				'servicemagic.com',
				'usdirectory.com',
				'yourlocalbusinessreviews.com',
				'zipweb.com'
			]

	for host in dumb_hosts:
		if host in uri:
			return None
	return uri












