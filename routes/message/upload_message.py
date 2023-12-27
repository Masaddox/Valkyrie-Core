from . import message
from time import time
from config import PATH_TO_DATABASE

from utils import database as db

from utils.xor import xor
from utils.last_id import last_id
from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.request_limiter import request_limiter
from utils.base64_dec_and_enc import base64_decode


@message.route(f"{PATH_TO_DATABASE}/uploadGJMessage20.php", methods=("POST", "GET"))
def upload_message():
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

    if account_id == recipient_id:
        return "-1"

    if not request_limiter(
        db.message, {"account_id": account_id}, limit_time=30
    ):
        return "-1"

    subject = request_get("subject")
    body = request_get("body")

    subject_decode = base64_decode(subject)
    body_decode = xor(base64_decode(body), "14251")

    if len(subject_decode) > 35 or len(subject_decode) == 0:
        return "-1"
    if len(body_decode) > 200 or len(body_decode) == 0:
        return "-1"

    try:
        message_state = db.account_stat.find_one({"_id": recipient_id})["message_state"]
    except:
        return "-1"

    if db.block_list.count_documents({"$or": [
        {"_id": recipient_id, "block_list": {"$in": (account_id,)}},
        {"_id": account_id, "block_list": {"$in": (recipient_id,)}}
    ]}) == 1:
        return "-1"

    if message_state == 1:
        if db.friend_list.count_documents({
            "_id": account_id, "friend_list": {"$in": (recipient_id,)}
        }) == 0:
            return "-1"
    elif message_state == 2:
        return "-1"

    db.message.insert_one({
        "_id": last_id(db.message),
        "account_id": account_id,
        "recipient_id": recipient_id,
        "subject": subject,
        "body": body,
        "is_read": 0,
        "upload_time": int(time())
    })

    db.account_stat.update_one({"_id": recipient_id}, {"$inc": {
        "missed_messages": 1
    }})

    return "1"
