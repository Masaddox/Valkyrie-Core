from . import score
from time import time
from config import PATH_TO_DATABASE
from pymongo import DESCENDING, ASCENDING

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.time_converter import time_conv
from utils.check_secret import check_secret
from utils.response_processing import resp_proc


@score.route(f"{PATH_TO_DATABASE}/getGJLevelScoresPlat.php", methods=("POST", "GET"))
def get_level_scores_platformer():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp2")

    if not check_password(
        account_id, password,
        is_gjp=False, is_gjp2=True
    ):
        return "-1"

    level_id = request_get("levelID", "int")
    daily_id = request_get("dailyID", "int")

    time_complete = request_get("time", "int")
    points = request_get("points", "int")
    mode = request_get("mode", "int")  # 0 - time, 1 - points

    if db.level.count_documents({
        "_id": level_id, "is_deleted": 0, "length": 5
    }) == 0:
        return "-1"

    if db.level_score.count_documents({
        "account_id": account_id,
        "level_id": level_id,
        "daily_id": daily_id
    }) == 0 and (time_complete > 0 or points > 0):
        db.level_score.insert_one({
            "level_id": level_id,
            "account_id": account_id,
            "time_complete": time_complete,
            "points": points,
            "daily_id": daily_id,
            "is_platformer": 1,
            "upload_time": int(time()),
            "update_time": int(time())
        })
    elif time_complete > 0 or points > 0:
        level_score = db.level_score.find({
            "account_id": account_id,
            "level_id": level_id,
            "daily_id": daily_id
        })[0]

        if level_score["time_complete"] > time_complete or level_score["points"] < points:  # update
            db.level_score.update_one({"_id": level_score["_id"]}, {"$set": {
                "time_complete": time_complete,
                "points": points,
                "update_time": int(time())
            }})

    # == getting scores ==
    score_type = request_get("type", "int")

    query = {
        "level_id": level_id,
        "daily_id": daily_id
    }

    match mode:
        case 0:
            sort = [("time_complete", ASCENDING), ("update_time", ASCENDING)]
        case _:
            sort = [("points", DESCENDING), ("update_time", ASCENDING)]

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

    counter = 1

    for i in level_scores:
        for j in users:
            if j["_id"] == i["account_id"]:
                user = j
                break
        else:
            continue

        if user["is_top_banned"] == 1 or user["is_banned"] == 1:
            continue

        glow = 2 if user["icon_glow"] == 1 else 0
        score_type = i["time_complete"] if mode == 0 else i["points"]

        single_response = {
            1: user["username"], 2: user["_id"], 9: user["icon_id"], 10: user["first_color"],
            11: user["second_color"], 51: user["third_color"], 14: user["icon_type"], 15: glow,
            16: user["_id"], 3: score_type, 6: counter, 42: time_conv(i["update_time"])
        }

        counter += 1

        response += resp_proc(single_response) + "|"

    return response
