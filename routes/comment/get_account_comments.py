from . import comment
from pymongo import DESCENDING
from config import PATH_TO_DATABASE

from utils import database as db

from utils.request_get import request_get
from utils.time_converter import time_conv
from utils.check_secret import check_secret
from utils.response_processing import resp_proc


@comment.route(f"{PATH_TO_DATABASE}/getGJAccountComments20.php", methods=("POST", "GET"))
def get_account_comments():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    account_id = request_get("accountID", "int")

    prefix = db.account_stat.find_one({"_id": account_id})["prefix"]
    prefix = prefix + " / " if prefix != "" else ""

    page = request_get("page", "int")

    offset = page * 10

    query = {
        "account_id": account_id
    }

    response = ""

    account_comments = tuple(db.account_comment.find(query).skip(offset).limit(10).sort([("_id", DESCENDING)]))

    for account_comment in account_comments:
        single_response = {
            2: account_comment["comment"], 4: account_comment["likes"],
            9: prefix + time_conv(account_comment["upload_time"]), 6: account_comment["_id"]
        }

        response += resp_proc(single_response, 2) + "|"

    response = response[:-1] + f"#{db.account_comment.count_documents(query)}:{offset}:10"

    return response
