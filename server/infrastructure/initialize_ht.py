import os

# TODO rename this... its only used in one place
def create_dir(mdir):
	try:
		print 'create_dir: ' + mdir
		os.makedirs(mdir)
	except Exception as e:
		assert('Could not make directory: ' + str(mdir))
	
