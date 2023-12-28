from . import misc
from time import time
from config import PATH_TO_DATABASE, PROTECTION_AGAINST_DISLIKE_BOTS

from utils import database as db

from utils.passwd import check_password
from utils.check_secret import check_secret
from utils.request_get import request_get, get_ip


@misc.route(f"{PATH_TO_DATABASE}/likeGJItem211.php", methods=("POST", "GET"))
def like_item():
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

    item_id = request_get("itemID", "int")
    item_type = request_get("type", "int")

    like = 1 if request_get("like", "int") != 0 else -1

    if db.action_like.count_documents({
        "item_id": item_id,
        "item_type": item_type,
        "account_id": account_id
    }) == 1:
        return "1"

    match item_type:
        case 1:  # Уровень
            coll = db.level
        case 2:  # Комментарий к уровню
            coll = db.level_comment
        case 3:  # Комментарий на аккаунте
            coll = db.account_comment
        case 4:  # Лит уровней
            coll = db.level_list
        case _:
            return "1"

    if coll.count_documents({
        "_id": item_id
    }) == 0:
        return "1"

    if item_type == 1 and coll.count_documents({
        "_id": item_id, "is_deleted": 0
    }) == 0:
        return "1"
    elif PROTECTION_AGAINST_DISLIKE_BOTS:
        if db.action_download.count_documents({
            "level_id": item_id, "account_id": account_id
        }) == 0:
            return "1"

    coll.update_one({"_id": item_id}, {"$inc": {"likes": like}})

    sample_action_like = {
        "item_id": item_id,
        "item_type": item_type,
        "account_id": account_id,
        "ip": get_ip(),
        "timestamp": int(time())
    }

    db.action_like.insert_one(sample_action_like)

    return "1"
