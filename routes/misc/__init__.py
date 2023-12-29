from flask import Blueprint


misc = Blueprint('misc', __name__)


from .like_item import *
from .sync_account import *
from .get_song_info import *
from .backup_account import *
from .get_account_url import *
from .request_user_access import *
from .get_custom_content_url import *
