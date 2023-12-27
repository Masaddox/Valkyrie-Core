from . import message
from pymongo import DESCENDING
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.time_converter import time_conv
from utils.check_secret import check_secret
from utils.response_processing import resp_proc


@message.route(f"{PATH_TO_DATABASE}/getGJMessages20.php", methods=("POST", "GET"))
def get_messages():
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

    page = request_get("page", "int")
    offset = page * 10

    is_sender = request_get("getSent", "int")

    query = {}
    response = ""

    query[
        "recipient_id" if is_sender == 0 else "account_id"
    ] = account_id

    messages = tuple(db.message.find(query).skip(offset).limit(10).sort([("_id", DESCENDING)]))

    for msg in messages:
        is_read = msg["is_read"] if is_sender == 0 else 1

        user_info = tuple(db.account_stat.find({
            "_id": msg["account_id"] if is_sender == 0 else msg["recipient_id"]
        }))

        prefix = user_info[0]["prefix"]
        prefix = prefix + " / " if prefix != "" else ""

        single_response = {
            6: user_info[0]["username"], 3: user_info[0]["_id"],
            2: user_info[0]["_id"], 1: msg["_id"], 4: msg["subject"],
            8: is_read, 9: is_sender, 7: prefix + time_conv(msg["upload_time"])
        }

        response += resp_proc(single_response) + "|"

    response = response[:-1] + f"#{db.message.count_documents(query)}:{page * 50}:{page * 50 + 50}"

    return response
