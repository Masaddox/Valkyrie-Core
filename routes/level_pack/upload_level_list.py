from time import time
from . import level_pack
from config import PATH_TO_DATABASE

from utils import database as db

from utils.last_id import last_id
from utils.regex import char_clean
from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.limit_check import new_limit_check
from utils.request_limiter import request_limiter
from utils.base64_dec_and_enc import base64_decode


@level_pack.route(f"{PATH_TO_DATABASE}/uploadGJLevelList.php", methods=("POST", "GET"))
def upload_level_list():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-100"

    account_id = request_get("accountID", "int")
    password = request_get("gjp2")

    if not check_password(
        account_id, password, is_gjp=False, is_gjp2=True
    ):
        return "-1"

    list_id = request_get("listID", "int")

    list_name = char_clean(request_get("listName"))
    list_name = list_name if list_name != "" else "Unnamed list"

    list_desc = request_get("listDesc")
    list_levels = request_get("listLevels", "list_int")

    if not bool(list_levels):
        return "-6"

    difficulty = request_get("difficulty", "int")  # -1 NA, 0 Auto, 1 Easy
    original = request_get("original", "int")

    unlisted = request_get("unlisted", "int")

    friend_only = 1 if unlisted == 1 else 0
    unlisted = 1 if unlisted >= 1 else 0

    if not new_limit_check(
        (1, len(list_name), 25), (0, len(base64_decode(list_desc)), 300), (1, len(list_levels), 75),
        (-1, difficulty, 10), (0, original, 99_999_999)
    ):
        return "-1"

    if list_id != 0:
        if db.level_list.count_documents({
            "_id": list_id, "account_id": account_id, "is_deleted": 0
        }) == 0:
            return "-1"

        if not request_limiter(
            db.level_list, {"account_id": account_id},
            date="update_time", limit_time=300
        ):
            return "-1"

        version = db.level_list.find_one({"_id": list_id})["version"]

        db.level_list.update_one({"_id": list_id}, {"$set": {
            "desc": list_desc,
            "levels": list_levels,
            "difficulty": difficulty,
            "version": version + 1,
            "update_time": int(time())
        }})

        return str(list_id)

    if not request_limiter(
        db.level_list, {"account_id": account_id},
        limit_time=300
    ):
        return "-1"

    list_id = last_id(db.level_list)
    username = db.account.find_one({"_id": account_id})["username"]

    db.level_list.insert_one({  # count_for_reward - Сколько нужно пройти уровней, чтобы получить награду
        "_id": list_id, "account_id": account_id, "name": list_name, "username": username, "desc": list_desc,
        "levels": list_levels, "version": 1, "downloads": 0, "likes": 0, "difficulty": difficulty,
        "diamonds": 0, "featured": 0, "count_for_reward": 0, "upload_time": int(time()), "update_time": 0,
        "rate_time": 0, "original": original, "unlisted": unlisted, "friend_only": friend_only, "is_deleted": 0
    })

    return str(list_id)
