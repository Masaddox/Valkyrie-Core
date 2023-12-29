from . import level
from time import time
from os.path import join
from threading import Thread
from pymongo import DESCENDING
from config import PATH_TO_DATABASE, PATH_TO_ROOT

from utils import database as db

from utils.xor import xor
from utils.passwd import check_password
from utils.check_secret import check_secret
from utils.response_processing import resp_proc
from utils.request_get import request_get, get_ip
from utils.difficulty_converter import demon_conv
from utils.base64_dec_and_enc import base64_encode
from utils.level_hashing import return_hash, return_hash2


def update_download_counter(level_id, account_id, ip):
    is_first_download = False

    if db.action_download.count_documents({
        "level_id": level_id, "account_id": account_id
    }) == 0:
        is_first_download = True

    if is_first_download:
        db.action_download.insert_one({
            "level_id": level_id,
            "account_id": account_id,
            "ip": ip,
            "timestamp": int(time())
        })
        db.level.update_one({"_id": level_id}, {"$inc": {"downloads": 1}})

    return is_first_download


@level.route(f"{PATH_TO_DATABASE}/downloadGJLevel22.php", methods=("POST", "GET"))
def download_level():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    level_id = request_get("levelID", "int")

    featured_id = 0
    is_featured = False

    if level_id < 0:  # Daily and Weekly
        type_daily = 0 if level_id == -1 else 1  # 0 = daily, 1 = weekly
        time_limit = 86400 if type_daily == 0 else 604800

        time_now = int(time())

        daily_level = tuple(db.daily_level.find({
            "timestamp": {"$lte": time_now},
            "type_daily": type_daily
        }).sort([("timestamp", DESCENDING)]).limit(1))

        if (daily_level[0]['timestamp'] + time_limit) - time_now <= -1:
            return "-1"

        level_id = daily_level[0]["level_id"]
        featured_id = daily_level[0]["daily_id"]

        featured_id = featured_id if type_daily == 0 else featured_id + 100001
        is_featured = True

    elif level_id == 0:
        return "-1"

    level_info = tuple(db.level.find({"_id": level_id, "is_deleted": 0}))

    user_info = ""
    response = ""

    for i in level_info:
        difficulty = 0

        if i["difficulty"] > 0:
            difficulty = i["difficulty"] * 10
            dd = 10
        else:
            dd = 0

        if i["legendary"] == 1:
            i["epic"] = 2
        if i["mythic"] == 1:
            i["epic"] = 3

        demon = "" if i["demon"] == 0 else 1
        auto = "" if i["auto"] == 0 else 1
        ldm = "" if i["ldm"] == 0 else 1

        official_song_id = i["song_id"] if bool(i["is_official_song"]) else 0
        custom_song_id = i["song_id"] if not bool(i["is_official_song"]) else 0

        with open(join(PATH_TO_ROOT, "data", "level", f"{str(level_id)}.level"), "r") as f:
            level_string = f.read()

        single_response = {
            1: i["_id"], 2: i["name"], 3: i["desc"], 4: level_string, 5: i["version"], 6: i["account_id"],
            8: dd, 9: difficulty, 10: i["downloads"], 12: official_song_id, 13: i["game_version"],
            14: i["likes"], 17: demon, 43: demon_conv(i["demon_type"]), 25: auto, 18: i["stars"],
            19: i["featured"], 42: i["epic"], 45: i["objects"], 15: i["length"], 30: i["original_id"],
            31: i["two_player"], 28: 0, 29: 0, 35: custom_song_id, 36: i["extra_string"], 37: i["coins"],
            38: i["is_silver_coins"], 39: 0, 46: 0, 47: 0, 40: ldm, 27: base64_encode(xor(str(
                i["password"]), "26364")), 52: i["song_ids"], 53: i["sfx_ids"], 57: i["ts"]
        }

        if is_featured:
            user_info = f"#{i['account_id']}:{i['username']}:{i['account_id']}"
            single_response.update({41: featured_id})

        hash_string = f"{i['account_id']},{i['stars']},{i['demon']},{i['_id']},{i['is_silver_coins']}," \
                      f"{i['featured']},{i['password']},{featured_id}"

        response = resp_proc(single_response) + f"#{return_hash2(level_string)}#{return_hash(hash_string)}"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    is_gjp2 = False

    if request_get("gjp2") != "":
        is_gjp2 = True
        password = request_get("gjp2")

    if check_password(
        account_id, password,
        is_gjp=not is_gjp2, is_gjp2=is_gjp2
    ):
        th = Thread(name="update_download_counter",
                    target=update_download_counter,
                    args=(level_id, account_id, get_ip(),))
        th.start()

    return response + user_info
