from . import message
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.time_converter import time_conv
from utils.check_secret import check_secret
from utils.response_processing import resp_proc


@message.route(f"{PATH_TO_DATABASE}/downloadGJMessage20.php", methods=("POST", "GET"))
def download_message():
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

    message_id = request_get("messageID", "int")

    try:
        msg = db.message.find({"_id": message_id})[0]
    except:
        return "-1"

    if msg["account_id"] != account_id and \
       msg["recipient_id"] != account_id:
        return "-1"

    user_info = db.account_stat.find({
        "_id": msg["account_id"] if account_id != msg["account_id"] else msg["recipient_id"]
    })[0]

    is_sender = 1 if msg["account_id"] == account_id else 0
    is_read = msg["is_read"] if is_sender == 0 else 1

    prefix = user_info["prefix"]
    prefix = prefix + " / " if prefix != "" else ""

    if is_sender == 0 and is_read == 0:
        db.message.update_one({"_id": message_id}, {"$set": {
            "is_read": 1
        }})
        db.account_stat.update_one({"_id": account_id}, {"$inc": {
            "missed_messages": -1
        }})

    response = {
        6: user_info["username"], 3: user_info["_id"], 2: user_info["_id"],
        1: message_id, 4: msg["subject"], 8: is_read, 9: is_sender, 5: msg["body"],
        7: prefix + time_conv(msg["upload_time"])
    }

    response = resp_proc(response)

    return response
