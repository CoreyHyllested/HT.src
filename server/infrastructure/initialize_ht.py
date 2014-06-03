import os

def create_dir(mdir):
	try:
		print 'create_dir: ' + mdir
		os.makedirs(mdir)
	except Exception as e:
		assert('Could not make directory: ' + str(mdir))
	
