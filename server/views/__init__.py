from flask import Blueprint

insprite_views = Blueprint('main', __name__)
from . import errors
