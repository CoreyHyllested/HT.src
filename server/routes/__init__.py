from flask import Blueprint

insprite_views = Blueprint('insprite', __name__)
insprite_tests = Blueprint('testing', __name__)
sc_views = Blueprint('sc', __name__)
print 'loading', __name__

