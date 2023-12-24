import json
from . import level
from time import time
from os.path import join
from sys import getsizeof
from config import PATH_TO_DATABASE, PATH_TO_ROOT

from utils import database as db

from utils.last_id import last_id
from utils.regex import char_clean
from utils.passwd import check_password
from utils.limit_check import limit_check
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.request_limiter import request_limiter
from utils.base64_dec_and_enc import base64_decode


MAXIMUM_LEVEL_SIZE = 10 * 1024 * 1024  # 10 MB
MINIMUM_NUMBER_BLOCKS = 0


@level.route(f"{PATH_TO_DATABASE}/uploadGJLevel21.php", methods=("POST", "GET"))
def upload_level():
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

    level_name = char_clean(request_get("levelName"))
    level_string = request_get("levelString")

    extra_string = request_get("extraString")
    level_length = request_get("levelLength", "int")
    audio_track = request_get("audioTrack", "int")
    level_desc = request_get("levelDesc")
    two_player = request_get("twoPlayer", "int")
    unlisted = request_get("unlisted", "int")
    password = request_get("password")
    original = request_get("original", "int")
    objects = request_get("objects", "int")
    song_id = request_get("songID", "int")
    coins = request_get("coins", "int")
    ldm = request_get("ldm", "int")

    if getsizeof(level_string) > MAXIMUM_LEVEL_SIZE:
        return "-1"

    if len(level_name) == 0 or len(level_string) == 0:
        return "-1"

    password = 1 if (password == "1") or (len(password) == 7) else 0

    if not limit_check(
        (level_length, 4), (len(base64_decode(level_desc)), 140), (two_player, 1),
        (unlisted, 1), (len(str(original)), 6), (coins, 3), (ldm, 1), (len(level_name), 20)
    ):
        return "-1"

    if limit_check((objects, MINIMUM_NUMBER_BLOCKS)) or objects <= 0:
        return "-1"

    if db.song.count_documents({
        "_id": song_id
    }) == 0 and song_id != 0:
        return "-1"

    is_official_song = 1 if song_id <= 0 else 0

    song_id = audio_track if bool(is_official_song) else song_id
    level_id = request_get("levelID", "int")

    if level_id == 0:
        if not request_limiter(
            db.level, {"account_id": account_id}, limit_time=300
        ):
            return "-1"

        level_id = last_id(db.level)

        with open(join(
            PATH_TO_ROOT, "data", "level", f"{str(level_id)}.level"
        ), "w") as file:
            file.write(level_string)

        sample_level = {
            "_id": level_id, "account_id": account_id, "username": db.account.find_one({"_id": account_id})["username"],
            "name": level_name, "desc": level_desc, "likes": 0, "downloads": 0, "version": 1, "length": level_length,
            "objects": objects, "password": password, "extra_string": extra_string,
            "coins": coins, "is_silver_coins": 0, "difficulty": 0, "stars": 0, "featured": 0, "epic": 0,
            "auto": 0, "demon": 0, "demon_type": 0, "song_id": song_id, "is_official_song": is_official_song,
            "original_id": original, "two_player": two_player, "unlisted": unlisted, "ldm": ldm,
            "upload_time": int(time()), "update_time": 0, "rate_time": 0, "is_deleted": 0, "delete_prohibition": 0,
            "update_prohibition": 0
        }

        db.level.insert_one(sample_level)

        return str(level_id)

    elif db.level.count_documents({
        "_id": level_id, "account_id": account_id,
        "update_prohibition": 0, "is_deleted": 0
    }) == 1:
        if not request_limiter(
            db.level, {"_id": level_id, "account_id": account_id}, date="update_time", limit_time=300
        ):
            return "-1"

        single_level = tuple(db.level.find({"_id": level_id}))
        level_version = single_level[0]["version"]

        with open(join(
            PATH_TO_ROOT, "data", "level", f"{str(level_id)}.level"
        ), "r") as file:
            old_level_string = file.read()

        with open(join(
            PATH_TO_ROOT, "data", "level", f"{str(level_id)}.level"
        ), "w") as file:
            file.write(level_string)

        with open(join(
            PATH_TO_ROOT, "data", "level", "old", f"{str(level_id)}v{level_version}.old.level"
        ), "w") as file:
            file.write(old_level_string)

        with open(join(
                PATH_TO_ROOT, "data", "level", "old", f"{str(level_id)}v{level_version}.old.level.db"
        ), "w") as file:
            file.write(json.dumps(single_level[0]))

        db.level.update_one({"_id": level_id}, {"$set": {
            "desc": level_desc,
            "version": level_version + 1,
            "password": password,
            "song_id": song_id,
            "is_official_song": is_official_song,
            "two_player": two_player,
            "objects": objects,
            "coins": coins,
            "extra_string": extra_string,
            "update_time": int(time()),
            "ldm": ldm
        }})

        return str(level_id)

    return "-1"
