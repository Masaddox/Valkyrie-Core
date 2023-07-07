from . import level
from time import time
from pymongo import DESCENDING
from config import PATH_TO_DATABASE
from utils import check_secret, request_get as rg, database as db


@level.route(f"{PATH_TO_DATABASE}/getGJDailyLevel.php", methods=("POST", "GET"))
def get_daily_level():
    if not check_secret.main(
        rg.main("secret"), 1
    ):
        return "-1"

    time_now = int(time())

    type_daily = rg.main("weekly", "int")

    additional_id = 0 if type_daily == 0 else 100001
    time_limit = 86400 if type_daily == 0 else 604800

    daily_level = tuple(db.daily_level.find({
        "timestamp": {"$lte": time_now},
        "type_daily": type_daily
    }).sort([("timestamp", DESCENDING)]).limit(1))

    try:
        return f"{daily_level[0]['daily_id'] + additional_id}|{(daily_level[0]['timestamp'] + time_limit) - time_now}"
    except IndexError:
        return "-1"