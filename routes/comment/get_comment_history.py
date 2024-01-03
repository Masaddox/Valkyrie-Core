from . import comment
from pymongo import DESCENDING
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.time_converter import time_conv
from utils.check_secret import check_secret
from utils.check_version import check_version
from utils.response_processing import resp_proc
from utils.base64_dec_and_enc import base64_decode


@comment.route(f"{PATH_TO_DATABASE}/getGJCommentHistory.php", methods=("POST", "GET"))
def get_comment_history():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    target_account_id = request_get("userID", "int")

    account_id = request_get("accountID", "int")
    password = None

    is_gjp2 = False

    if request_get("gjp2") != "":
        is_gjp2 = True
        password = request_get("gjp2")

    if is_gjp2 is False and check_version() <= 21:
        pass

    elif not check_password(
        account_id, password,
        is_gjp=False, is_gjp2=True
    ):
        return "-1"

    show_comment_mode = db.account_stat.find_one({"_id": target_account_id})["comment_history_state"]
    # 0 - all, 1 - friends, 2 - me

    if check_version() >= 22:
        match show_comment_mode:
            case 1:
                if account_id == target_account_id:
                    pass
                elif db.friend_list.count_documents(
                    {"_id": account_id, "friend_list": {"$in": [target_account_id]}}
                ) == 0:
                    return "-1"
            case 2:
                if account_id != target_account_id:
                    return "-1"
            case _:
                pass

    page = request_get("page", "int")
    offset = page * 10

    sort_mode = request_get("mode", "int")
    sort = [("_id", DESCENDING)] if sort_mode == 0 else [("likes", DESCENDING)]

    query = {
        "account_id": target_account_id
    }

    comments = tuple(db.level_comment.find(query).skip(offset).limit(10).sort(sort))

    response = ""

    for i in comments:
        user_info = tuple(db.account_stat.find({"_id": target_account_id}))

        prefix = user_info[0]["prefix"]
        prefix = prefix + " / " if prefix != "" else ""

        glow = user_info[0]["icon_glow"]
        glow = 2 if glow == 1 else glow

        single_comment_response = {
            1: i["level_id"], 2: base64_decode(i["comment"]), 3: target_account_id, 4: i["likes"],
            7: 0, 10: i["percent"], 9: prefix + time_conv(i["upload_time"]),
            6: i["_id"], 11: user_info[0]["mod_badge"]
        }

        if user_info[0]["comment_color"] != "":
            single_comment_response.update({12: user_info[0]["comment_color"]})

        response += resp_proc(single_comment_response, 2) + ":"

        single_user_response = {
            1: user_info[0]["username"], 9: user_info[0]["icon_id"], 10: user_info[0]["first_color"],
            11: user_info[0]["second_color"], 14: user_info[0]["icon_type"], 15: glow, 16: target_account_id
        }

        response += resp_proc(single_user_response, 2) + "|"

    response = response + f"#{db.level_comment.count_documents(query)}:{offset}:10"

    return response
