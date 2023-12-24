from . import user
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.response_processing import resp_proc


@user.route(f"{PATH_TO_DATABASE}/getGJUserInfo20.php", methods=("POST", "GET"))
def get_user_info():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    target_account_id = request_get("targetAccountID", "int")

    is_account_owner = False
    response = {}

    if target_account_id <= 0 or account_id <= 0:
        return "-1"

    account_stat_info = tuple(db.account_stat.find({"_id": target_account_id}))

    if not bool(account_stat_info):
        return "-1"

    for i in account_stat_info:
        response = {
            1: i["username"], 2: target_account_id, 13: i["secret_coins"], 17: i["user_coins"], 10: i["first_color"],
            11: i["second_color"], 3: i["stars"], 46: i["diamonds"], 4: i["demons"], 8: i["creator_points"],
            18: i["message_state"], 19: i["friends_state"], 50: i["comment_history_state"], 20: i["youtube"],
            21: i["icon_cube"], 22: i["icon_ship"], 23: i["icon_ball"], 24: i["icon_ufo"], 25: i["icon_wave"],
            26: i["icon_robot"], 28: i["icon_glow"], 43: i["icon_spider"], 48: 0, 30: i["global_rank"],
            16: target_account_id
        }

    if check_password(
        account_id, password
    ):
        is_account_owner = True

    if is_account_owner and account_id != target_account_id:

        if db.friend_list.count_documents({
            "_id": account_id, "friend_list": {"$in": (target_account_id,)}
        }) == 1:
            response.update({31: 1})

        elif db.friend_req.count_documents({
            "account_id": account_id, "recipient_id": target_account_id
        }) == 1:
            response.update({31: 4})

        elif db.friend_req.count_documents({
            "account_id": target_account_id, "recipient_id": account_id
        }) == 1:
            response.update({31: 3})

        else:
            response.update({31: 0})

    response.update({
        44: account_stat_info[0]["twitter"], 45: account_stat_info[0]["twitch"],
        49: account_stat_info[0]["mod_level"]
    })

    if is_account_owner and account_id == target_account_id:
        response.update({
            38: account_stat_info[0]["missed_messages"], 39: account_stat_info[0]["friend_requests"], 40: 0
        })

    response.update({
        29: 1
    })

    return resp_proc(response)
