from flask import Blueprint


score = Blueprint('score', __name__)


from .get_scores import *
from .get_level_scores import *
from .get_level_scores_platformer import *
