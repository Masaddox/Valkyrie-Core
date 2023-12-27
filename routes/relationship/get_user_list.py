from . import relationship
from pymongo import ASCENDING
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.response_processing import resp_proc


@relationship.route(f"{PATH_TO_DATABASE}/getGJUserList20.php", methods=("POST", "GET"))
def get_user_list():
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
    
    list_type = request_get("type", "int")

    query = {
        "_id": account_id
    }

    user_ids = tuple(db.friend_list.find(query)) \
        if list_type == 0 else tuple(db.block_list.find(query))

    list_str = "friend_list" if list_type == 0 else "block_list"

    if not bool(user_ids) or not bool(user_ids[0][list_str]):
        return "-2"

    users = tuple(db.account_stat.find({"_id": {"$in": user_ids[0][list_str]}}).sort([("username", ASCENDING)]))
    response = ""

    for user in users:
        glow = 2 if user["icon_glow"] == 1 else 0

        single_response = {
            1: user["username"], 2: user["_id"], 9: user["icon_id"],
            10: user["first_color"], 11: user["second_color"], 14: user["icon_type"],
            15: glow, 16: user["_id"], 18: user["message_state"], 41: ""
        }

        response += resp_proc(single_response) + "|"

    response = response[:-1]

    return response
