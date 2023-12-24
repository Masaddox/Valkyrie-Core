from . import misc
from config import PATH_TO_DATABASE, PROTECTION_AGAINST_DISLIKE_BOTS

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret


@misc.route(f"{PATH_TO_DATABASE}/likeGJItem211.php", methods=("POST", "GET"))
def like_item():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    item_id = request_get("itemID", "int")
    item_type = request_get("type", "int")

    like = 1 if request_get("like", "int") != 0 else -1

    if not check_password(
        account_id, password
    ):
        return "1"

    if db.action_like.count_documents({
        "item_id": item_id,
        "item_type": item_type,
        "account_id": account_id
    }) == 1:
        return "1"

    if item_type == 1:  # Уровень
        coll = db.level
    elif item_type == 2:  # Комментарий к уровню
        coll = db.level_comment
    elif item_type == 3:  # Комментарий на аккаунте
        coll = db.account_comment
    else:
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
    }

    db.action_like.insert_one(sample_action_like)

    return "1"
