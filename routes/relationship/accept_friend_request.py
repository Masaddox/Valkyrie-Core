from . import relationship
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret


@relationship.route(f"{PATH_TO_DATABASE}/acceptGJFriendRequest20.php", methods=("POST", "GET"))
def accept_friend_request():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    sender_id = request_get("targetAccountID", "int")
    request_id = request_get("requestID", "int")

    if not check_password(
        account_id, password
    ):
        return "-1"

    if db.friend_req.count_documents({
        "_id": request_id,
        "account_id": sender_id,
        "recipient_id": account_id
    }) == 0:
        return "-1"

    if db.friend_list.count_documents({
        "_id": account_id, "friend_list": {"$size": {"$gte": 100}}
    }) == 1:
        return "-1"

    db.account_stat.update_one({"_id": account_id}, {"$inc": {
        "friend_requests": -1
    }})

    if db.friend_list.count_documents({
        "_id": account_id
    }) == 0:
        db.friend_list.insert_one({
            "_id": account_id, "friend_list": []
        })

    db.friend_list.update_one({"_id": account_id}, {"$push": {"friend_list": sender_id}})

    if db.friend_list.count_documents({
        "_id": sender_id
    }) == 0:
        db.friend_list.insert_one({
            "_id": sender_id, "friend_list": []
        })

    db.friend_list.update_one({"_id": sender_id}, {"$push": {"friend_list": account_id}})

    db.friend_req.delete_one({"_id": request_id})

    return "1"
