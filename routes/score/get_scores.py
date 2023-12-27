from . import score
from pymongo import DESCENDING
from config import PATH_TO_DATABASE, REDIS_PREFIX

from utils import database as db

from utils.redis_db import client as rd
from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.response_processing import resp_proc

SCORES_LIFETIME = 3600


def upload_scores(score_type="top"):  # for cron
    query = {"is_top_banned": 0}

    limit = 100
    sort = [("stars", DESCENDING)]

    if score_type == "top":
        query["stars"] = {"$gte": 10}
    elif score_type == "creators":
        query["creator_points"] = {"$gt": 0}
        sort = [("creator_points", DESCENDING)]

    response = ""

    users = db.account_stat.find(query).limit(limit)
    users.sort(sort)

    counter = 1

    for user in users:
        glow = 2 if user["icon_glow"] == 1 else 0

        single_response = {
            1: user["username"], 2: user["_id"], 13: user["secret_coins"], 17: user["user_coins"],
            6: counter, 9: user["icon_id"], 10: user["first_color"], 11: user["second_color"],
            14: user["icon_type"], 15: glow, 16: user["_id"], 3: user["stars"], 8: user["creator_points"],
            46: user["diamonds"], 4: user["demons"]
        }

        counter += 1
        response += resp_proc(single_response) + "|"

    rd.set(f"{REDIS_PREFIX}:top:{score_type}", response, SCORES_LIFETIME)

    return response


@score.route(f"{PATH_TO_DATABASE}/getGJScores20.php", methods=("POST", "GET"))
def get_scores():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "1"

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
        return "1"

    score_type = request_get("type")

    if score_type == "" or score_type == "relative":
        score_type = "top"

    if score_type != "friends":
        cache = rd.get(f"{REDIS_PREFIX}:top:{score_type}")
        if cache is not None:
            return cache

    query = {"is_top_banned": 0}

    limit = 100
    sort = [("stars", DESCENDING)]

    if score_type == "top":

        query["stars"] = {"$gte": 10}

    elif score_type == "creators":

        query["creator_points"] = {"$gt": 0}
        sort = [("creator_points", DESCENDING)]

    elif score_type == "friends":

        return "1"

    else:

        return "-1"

    response = ""

    users = db.account_stat.find(query).limit(limit)
    users.sort(sort)

    counter = 1

    for user in users:
        glow = 2 if user["icon_glow"] == 1 else 0

        single_response = {
            1: user["username"], 2: user["_id"], 13: user["secret_coins"], 17: user["user_coins"],
            6: counter, 9: user["icon_id"], 10: user["first_color"], 11: user["second_color"],
            14: user["icon_type"], 15: glow, 16: user["_id"], 3: user["stars"], 8: user["creator_points"],
            46: user["diamonds"], 4: user["demons"]
        }

        counter += 1
        response += resp_proc(single_response) + "|"

    if score_type != "friends":
        rd.set(f"{REDIS_PREFIX}:top:{score_type}", response, SCORES_LIFETIME)

    return response
