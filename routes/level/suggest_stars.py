from . import level
from time import time
from flask import abort
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.difficulty_converter import diff_conv


FEATURED_CONV = {
    0: {"featured": 0, "epic": 0, "legendary": 0, "mythic": 0},
    1: {"featured": 1, "epic": 0, "legendary": 0, "mythic": 0},
    2: {"featured": 1, "epic": 1, "legendary": 0, "mythic": 0},
    3: {"featured": 1, "epic": 0, "legendary": 1, "mythic": 0},
    4: {"featured": 1, "epic": 0, "legendary": 0, "mythic": 1},
}


@level.route(f"{PATH_TO_DATABASE}/suggestGJStars.php", methods=("POST", "GET"))
@level.route(f"{PATH_TO_DATABASE}/suggestGJStars20.php", methods=("POST", "GET"))
def suggest_stars():
    if not check_secret(
        request_get("secret"), 3
    ):
        abort(500)

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    is_gjp2 = False

    if request_get("gjp2") != "":
        is_gjp2 = True
        password = request_get("gjp2")

    if not check_password(
        account_id, password, is_gjp=not is_gjp2, is_gjp2=is_gjp2
    ):
        abort(500)

    level_id = request_get("levelID", "int")

    stars = request_get("stars", "int")
    featured = request_get("feature", "int")

    if db.role_assign.count_documents({
        "_id": account_id
    }) == 0:
        return "-2"

    if db.level.count_documents({
        "_id": level_id, "is_deleted": 0
    }) == 0:
        abort(500)

    role_id = db.role_assign.find_one({"_id": account_id})["role_id"]
    access = db.role.find_one({"_id": role_id})["command_access"]["suggest_stars"]

    query_level = {"rate_time": int(time())} | FEATURED_CONV[featured]

    match access:
        case 1:
            db.suggest.insert_one({
                "account_id": account_id,
                "username": db.account_stat.find_one({"_id": account_id})["username"],
                "level_id": level_id,
                "stars": stars,
                "timestamp": int(time())
            } | FEATURED_CONV[featured])

            return "1"

        case 2:
            if stars == 1:  # Авто
                query_level.update({
                    "auto": 1,
                    "stars": 1,
                    "demon": 0,
                    "demon_type": 0,
                    "difficulty": 1
                })
            elif 1 < stars < 10:
                query_level.update({
                    "auto": 0,
                    "stars": stars,
                    "demon": 0,
                    "demon_type": 0,
                    "difficulty": diff_conv(stars)
                })
            elif stars == 10:
                query_level.update({
                    "auto": 0,
                    "stars": 10,
                    "demon": 1,
                    "demon_type": 3,
                    "difficulty": 5
                })

        case _:
            abort(500)

    db.level.update_one({"_id": level_id}, {"$set": query_level})

    return "1"
