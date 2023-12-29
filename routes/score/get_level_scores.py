from . import score
from time import time
from icecream import ic
from config import PATH_TO_DATABASE
from pymongo import DESCENDING, ASCENDING

from utils import database as db

from utils.xor import xor
from utils.passwd import check_password
from utils.limit_check import limit_check
from utils.request_get import request_get
from utils.time_converter import time_conv
from utils.check_secret import check_secret
from utils.response_processing import resp_proc
from utils.base64_dec_and_enc import base64_decode


@score.route(f"{PATH_TO_DATABASE}/getGJLevelScores211.php", methods=("POST", "GET"))
def get_level_scores():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    is_gjp2 = False

    if request_get("gjp2") != "":
        is_gjp2 = True
        password = request_get("gjp2")

    if not check_password(
        account_id, password,
        is_gjp=not is_gjp2, is_gjp2=is_gjp2
    ):
        return "-1"

    level_id = request_get("levelID", "int")

    percent = request_get("percent", "int")
    attempts = request_get("s1", "int") - 8354
    clicks = request_get("s2", "int") - 3991
    attempt_time = request_get("s3", "int") - 4085

    progresses = request_get("s6")
    if progresses != "":
        progresses = xor(base64_decode(progresses), "41274")

    coins = request_get("s9", "int") - 5819
    daily_id = request_get("s10", "int")

    if not limit_check(
        (percent, 100), (coins, 3)
    ):
        return "-1"

    if db.level.count_documents({
        "_id": level_id, "is_deleted": 0
    }) == 0:
        return "-1"

    level = db.level.find({"_id": level_id})[0]

    if coins > level["coins"] and level["length"] >= 5:
        return "-1"

    if db.level_score.count_documents({
        "account_id": account_id,
        "level_id": level_id,
        "daily_id": daily_id
    }) == 0 and percent > 0:
        db.level_score.insert_one({
            "level_id": level_id,
            "account_id": account_id,
            "percent": percent,
            "attempts": attempts,
            "attempt_time": attempt_time,
            "clicks": clicks,
            "progresses": progresses,
            "coins": coins,
            "daily_id": daily_id,
            "is_platformer": 0,
            "upload_time": int(time()),
            "update_time": int(time())
        })
    elif percent > 0:
        level_score = db.level_score.find({
            "account_id": account_id,
            "level_id": level_id,
            "daily_id": daily_id
        })[0]

        if level_score["percent"] < percent or level_score["coins"] < coins:  # update
            db.level_score.update_one({"_id": level_score["_id"]}, {"$set": {
                "percent": percent,
                "attempts": attempts,
                "attempt_time": attempt_time,
                "clicks": clicks,
                "progresses": progresses,
                "coins": coins,
                "update_time": int(time())
            }})

    # == getting scores ==
    score_type = request_get("type", "int")

    query = {
        "level_id": level_id,
        "daily_id": daily_id
    }
    sort = [("percent", DESCENDING), ("coins", DESCENDING), ("update_time", ASCENDING)]

    response = ""

    match score_type:
        case 0:  # Friends
            try:
                friend_list = db.friend_list.find_one({"_id": account_id})["friend_list"]
            except IndexError:
                return ""
            query["account_id"] = {"$in": friend_list + [account_id]}

        case 1:  # Top
            pass

        case 2:  # Top week
            query["update_time"] = {"$gt": int(time()) - (7 * 24 * 60 * 60)}

    level_scores = tuple(db.level_score.find(query).limit(50).sort(sort))
    users = tuple(db.account_stat.find({"_id": {"$in": [i["account_id"] for i in level_scores]}}))

    for i in level_scores:
        for j in users:
            if j["_id"] == i["account_id"]:
                user = j
                break
        else:
            continue

        if user["is_top_banned"] == 1 or user["is_banned"] == 1:
            continue

        if i["percent"] == 100:
            place = 1
        elif i["percent"] > 75:
            place = 2
        else:
            place = 3

        glow = 2 if user["icon_glow"] == 1 else 0

        single_response = {
            1: user["username"], 2: user["_id"], 9: user["icon_id"], 10: user["first_color"],
            11: user["second_color"], 51: user["third_color"], 14: user["icon_type"], 15: glow,
            16: user["_id"], 3: i["percent"], 6: place, 13: i["coins"], 42: time_conv(i["update_time"])
        }

        response += resp_proc(single_response) + "|"

    return response
