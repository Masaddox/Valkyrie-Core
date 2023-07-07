from . import level
from time import time
from flask import abort
from config import PATH_TO_DATABASE
from utils import passwd, check_secret, request_get as rg, \
    database as db, difficulty_converter as dc


@level.route(f"{PATH_TO_DATABASE}/suggestGJStars.php", methods=("POST", "GET"))
@level.route(f"{PATH_TO_DATABASE}/suggestGJStars20.php", methods=("POST", "GET"))
def suggest_stars():
    if not check_secret.main(
        rg.main("secret"), 3
    ):
        abort(500)

    account_id = rg.main("accountID", "int")
    password = rg.main("gjp")

    level_id = rg.main("levelID", "int")

    stars = rg.main("stars", "int")
    featured = rg.main("feature", "int")

    if not passwd.check_password(
        account_id, password
    ):
        abort(500)

    if db.role_assign.count_documents({
        "_id": account_id
    }) == 0:
        return "-2"

    if db.level.count_documents({
        "_id": level_id, "is_deleted": 0
    }) == 0:
        abort(500)

    role_id = db.role_assign.find_one({"_id": account_id})["role_id"]
    mod_level = db.role.find_one({"_id": role_id})["mod_level"]

    query_level = {"rate_time": int(time()), "delete_prohibition": 1}

    if mod_level == 1:

        db.suggest.insert_one({
            "account_id": account_id,
            "level_id": level_id,
            "stars": stars,
            "featured": featured,
            "timestamp": int(time())
        })

        return "1"

    elif mod_level >= 2:

        query_level["featured"] = 1 if bool(featured) else 0

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
                "difficulty": dc.diff_conv(stars)
            })
        elif stars == 10:
            query_level.update({
                "auto": 0,
                "stars": 10,
                "demon": 1,
                "demon_type": 3,
                "difficulty": 5
            })

    else:
        abort(500)

    db.level.update_one({"_id": level_id}, {"$set": query_level})

    return "1"