from flask import Blueprint

insprite_views = Blueprint('insprite', __name__)
insprite_tests = Blueprint('testing', __name__)
sc_users = Blueprint('sc_users', __name__)
sc_ebody = Blueprint('sc_ebody', __name__)
print 'loading', __name__

