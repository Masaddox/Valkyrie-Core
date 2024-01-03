from . import reward
from flask import abort
from datetime import datetime
from random import randint, choice
from config import PATH_TO_DATABASE

from utils import database as db

from utils.xor import xor
from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.level_hashing import return_hash4
from utils.base64_dec_and_enc import base64_decode, base64_encode


DAILY_CHESTS = {
    "small": {
        "orbs": (500, 1000),
        "diamonds": (1, 5),
        "items": list(range(1, 15)),  # [1, 2, ... 14]
        "keys": (1, 10),
        "wait_time": 30 * 60
    },
    "big": {
        "orbs": (1000, 4000),
        "diamonds": (5, 40),
        "items": list(range(1, 15)),
        "keys": (10, 50),
        "wait_time": 2 * 60 * 60
    }
}


@reward.route(f"{PATH_TO_DATABASE}/getGJRewards.php", methods=("POST", "GET"))
def get_rewards():
    if not check_secret(
            request_get("secret"), 1
    ):
        abort(500)

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
        abort(500)

    udid = request_get("udid")
    reward_type = request_get("rewardType", "int")

    chk = request_get("chk")
    chk = xor(base64_decode(chk[5:]), "59182")

    now = int(datetime.now().timestamp() + 100)

    small_chest_diff = now - db.account_stat.find_one({"_id": account_id})["small_chest_time"]
    big_chest_diff = now - db.account_stat.find_one({"_id": account_id})["big_chest_time"]

    small_chest_string = (f"{randint(*DAILY_CHESTS["small"]["orbs"])},{randint(*DAILY_CHESTS["small"]["diamonds"])},"
                          f"{choice(DAILY_CHESTS["small"]["items"])},{randint(*DAILY_CHESTS["small"]["keys"])}")
    big_chest_string = (f"{randint(*DAILY_CHESTS["big"]["orbs"])},{randint(*DAILY_CHESTS["big"]["diamonds"])},"
                        f"{choice(DAILY_CHESTS["big"]["items"])},{randint(*DAILY_CHESTS["big"]["keys"])}")

    small_chest_left = max(0, DAILY_CHESTS["small"]["wait_time"] - small_chest_diff)
    big_chest_left = max(0, DAILY_CHESTS["big"]["wait_time"] - big_chest_diff)

    match reward_type:
        case 1:  # small chest
            if small_chest_left != 0:
                return "-1"

            db.account_stat.update_one({"_id": account_id}, {"$inc": {"small_chest_counter": 1}})
            db.account_stat.update_one({"_id": account_id}, {"$set": {"small_chest_time": now}})

            small_chest_left = DAILY_CHESTS["small"]["wait_time"]

        case 2:  # big chest
            if big_chest_left != 0:
                return "-1"

            db.account_stat.update_one({"_id": account_id}, {"$inc": {"big_chest_counter": 1}})
            db.account_stat.update_one({"_id": account_id}, {"$set": {"big_chest_time": now}})

            big_chest_left = DAILY_CHESTS["big"]["wait_time"]

    small_chest_counter = db.account_stat.find_one({"_id": account_id})["small_chest_counter"]
    big_chest_counter = db.account_stat.find_one({"_id": account_id})["big_chest_counter"]

    response = base64_encode(xor(
        f"1:{account_id}:{chk}:{udid}:{account_id}:{small_chest_left}:{small_chest_string}:{small_chest_counter}:"
        f"{big_chest_left}:{big_chest_string}:{big_chest_counter}:{reward_type}", "59182"))

    response_hash = return_hash4(response)

    return f"vcore{response}|{response_hash}"
