from . import relationship
from pymongo import DESCENDING
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.time_converter import time_conv
from utils.check_secret import check_secret
from utils.response_processing import resp_proc


@relationship.route(f"{PATH_TO_DATABASE}/getGJFriendRequests20.php", methods=("POST", "GET"))
def get_friend_requests():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    if not check_password(
        account_id, password
    ):
        return "-1"

    page = request_get("page", "int")
    offset = page * 10

    type_request = request_get("getSent", "int")

    query = {}
    response = ""

    query[
        "recipient_id" if type_request == 0 else "account_id"
    ] = account_id

    friend_reqs = tuple(db.friend_req.find(query).skip(offset).limit(10).sort([("_id", DESCENDING)]))

    for req in friend_reqs:
        user_info = tuple(db.account_stat.find({
            "_id": req["account_id"] if type_request == 0 else req["recipient_id"]
        }))

        glow = 2 if user_info[0]["icon_glow"] == 1 else 0

        single_response = {
            1: user_info[0]["username"], 2: user_info[0]["_id"], 9: user_info[0]["icon_id"],
            10: user_info[0]["first_color"], 11: user_info[0]["second_color"], 14: user_info[0]["icon_type"],
            15: glow, 16: user_info[0]["_id"], 32: req["_id"], 35: req["comment"], 41: 1,
            37: time_conv(req["timestamp"])
        }

        response += resp_proc(single_response) + "|"

    response = response[:-1] + f"#:{page * 20}:20"

    return response
