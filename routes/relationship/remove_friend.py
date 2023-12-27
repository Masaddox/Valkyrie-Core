from . import relationship
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret


@relationship.route(f"{PATH_TO_DATABASE}/removeGJFriend20.php", methods=("POST", "GET"))
def remove_friend():
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

    target_id = request_get("targetAccountID", "int")

    if db.friend_list.count_documents({
        "_id": account_id, "friend_list": {"$in": (target_id,)}
    }) == 0:
        return "-1"

    db.friend_list.update_one({"_id": account_id}, {"$pull": {"friend_list": target_id}})
    db.friend_list.update_one({"_id": target_id}, {"$pull": {"friend_list": account_id}})

    return "1"
