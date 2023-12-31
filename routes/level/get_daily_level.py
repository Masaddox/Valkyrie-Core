from . import level
from time import time
from pymongo import DESCENDING
from config import PATH_TO_DATABASE

from utils import database as db

from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.check_version import check_version


@level.route(f"{PATH_TO_DATABASE}/getGJDailyLevel.php", methods=("POST", "GET"))
def get_daily_level():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    time_now = int(time())
    type_daily = 0

    if check_version() <= 21:
        type_daily = request_get("weekly", "int")
    elif check_version() >= 22:
        type_daily = request_get("type", "int")

    additional_id = 0 if type_daily == 0 else 100001
    time_limit = 86400 if type_daily == 0 else 604800

    daily_level = tuple(db.daily_level.find({
        "timestamp": {"$lte": time_now},
        "type_daily": type_daily
    }).sort([("timestamp", DESCENDING)]).limit(1))

    try:
        time_left = (daily_level[0]['timestamp'] + time_limit) - time_now

        if time_left <= -1:
            return "-1"

        return f"{daily_level[0]['daily_id'] + additional_id}|{time_left}"
    except IndexError:
        return "-1"
