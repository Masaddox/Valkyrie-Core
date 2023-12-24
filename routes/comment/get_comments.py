from . import comment
from pymongo import DESCENDING
from config import PATH_TO_DATABASE

from utils import database as db

from utils.request_get import request_get
from utils.time_converter import time_conv
from utils.check_secret import check_secret
from utils.response_processing import resp_proc
from utils.base64_dec_and_enc import base64_decode


@comment.route(f"{PATH_TO_DATABASE}/getGJComments21.php", methods=("POST", "GET"))
def get_comments():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    level_id = request_get("levelID", "int")

    page = request_get("page", "int")
    offset = page * 10

    sort_mode = request_get("mode", "int")
    sort = [("_id", DESCENDING)] if sort_mode == 0 else [("likes", DESCENDING)]

    query = {
        "level_id": level_id
    }

    comments = tuple(db.level_comment.find(query).skip(offset).limit(10).sort(sort))

    response = ""

    for i in comments:
        account_id = i["account_id"]
        user_info = tuple(db.account_stat.find({"_id": account_id}))

        prefix = user_info[0]["prefix"]
        prefix = prefix + " / " if prefix != "" else ""

        glow = user_info[0]["icon_glow"]
        glow = 2 if glow == 1 else glow

        single_comment_response = {
            2: base64_decode(i["comment"]), 3: account_id, 4: i["likes"],
            7: 0, 10: i["percent"], 9: prefix + time_conv(i["upload_time"]),
            6: i["_id"], 11: user_info[0]["mod_level"]
        }

        if user_info[0]["comment_color"] != "":
            single_comment_response.update({12: user_info[0]["comment_color"]})

        response += resp_proc(single_comment_response, 2)[:-1] + ":"

        single_user_response = {
            1: user_info[0]["username"], 9: user_info[0]["icon_id"], 10: user_info[0]["first_color"],
            11: user_info[0]["second_color"], 14: user_info[0]["icon_type"], 15: glow, 16: account_id
        }

        response += resp_proc(single_user_response, 2) + "|"

    response = response + f"#{db.level_comment.count_documents(query)}:{offset}:10"

    return response
