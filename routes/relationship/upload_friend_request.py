from time import time
from . import relationship
from config import PATH_TO_DATABASE

from utils import database as db

from utils.last_id import last_id
from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.base64_dec_and_enc import base64_decode


@relationship.route(f"{PATH_TO_DATABASE}/uploadFriendRequest20.php", methods=("POST", "GET"))
def upload_friend_request():
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

    recipient_id = request_get("toAccountID", "int")
    comment = request_get("comment")

    if len(base64_decode(comment)) > 140:
        return "-1"

    if account_id == recipient_id:
        return "-1"

    if db.account_stat.count_documents(
        {"account_id": recipient_id, "friends_state": 1}
    ) == 1:
        return "-1"

    if db.friend_req.count_documents({"$or": [
        {"account_id": account_id, "recipient_id": recipient_id},
        {"account_id": recipient_id, "recipient_id": account_id}
    ]}) == 1:
        return "-1"

    if db.friend_list.count_documents({
        "_id": account_id, "friend_list": {"$in": [recipient_id]}
    }) == 1:
        return "-1"

    if db.block_list.count_documents({"$or": [
        {"_id": account_id, "block_list": {"$in": [recipient_id]}},
        {"_id": recipient_id, "block_list": {"$in": [account_id]}},
    ]}) == 1:
        return "-1"

    db.friend_req.insert_one({
        "_id": last_id(db.friend_req),
        "account_id": account_id,
        "recipient_id": recipient_id,
        "comment": comment,
        "timestamp": int(time())
    })

    db.account_stat.update_one({"_id": recipient_id}, {"$inc": {
        "friend_requests": 1
    }})

    return "1"
