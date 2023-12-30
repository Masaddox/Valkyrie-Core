from . import level
from time import time
from config import PATH_TO_DATABASE
from pymongo import DESCENDING, ASCENDING

from utils import database as db

from utils.passwd import check_password
from utils.check_secret import check_secret
from utils.level_hashing import return_hash
from utils.check_version import check_version
from utils.response_processing import resp_proc
from utils.request_get import request_get, get_ip
from utils.difficulty_converter import demon_conv


def bool_chk(x): return x == "1"


def int_conv(x):
    try:
        return int(x)
    except TypeError:
        return -1
    except ValueError:
        return -1


@level.route(f"{PATH_TO_DATABASE}/getGJLevels21.php", methods=("POST", "GET"))
def get_level():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    is_gjp2 = False
    confirmed_account = False

    gd_version = check_version()

    if request_get("gjp2") != "":
        is_gjp2 = True
        password = request_get("gjp2")

    if not check_password(
        account_id, password,
        is_gjp=not is_gjp2, is_gjp2=is_gjp2
    ):
        if gd_version >= 22:
            return "-1"

        confirmed_account = False
    else:
        confirmed_account = True

    gauntlet = request_get("gauntlet", "int")
    gauntlet_bool = "" if gauntlet <= 0 else "1"

    demon_filter = request_get("demonFilter", "int")
    difficulty = request_get("diff")
    type_pack = request_get("type")
    search = request_get("str")
    long = request_get("len")

    star = request_get("star")
    no_star = request_get("noStar")
    featured = request_get("featured")
    epic = request_get("epic")
    legendary = request_get("legendary")
    mythic = request_get("mythic")

    original = request_get("original")
    two_player = request_get("twoPlayer")
    silver_coins = request_get("coins")

    song_id = request_get("song")
    is_custom_song = request_get("customSong")

    uncompleted = request_get("uncompleted", "int")
    only_completed = request_get("onlyCompleted", "int")
    completed_levels = request_get("completedLevels")

    page = request_get("page", "int")
    followed = request_get("followed")

    query = {
        "unlisted": 0,
        "is_deleted": 0,
        "$or": []
    }

    sort = [("likes", DESCENDING)]

    if gauntlet > 0:  # Гаунтлет уровни
        gauntlet_levels = db.gauntlet.find_one({"_id": gauntlet})["levels"].split(",")
        query["_id"] = {"$in": list(map(int_conv, gauntlet_levels))}

        sort = [("stars", ASCENDING), ("demon_type", ASCENDING)]
    else:
        if bool_chk(star):
            query["stars"] = {"$gt": 0}
        if bool_chk(no_star):
            query["stars"] = 0
        if bool_chk(featured):
            query["$or"].append({
                "featured": 1,
                "epic": 0,
                "legendary": 0,
                "mythic": 0
            })
        if bool_chk(epic):
            query["$or"].append(
                {"epic": 1}
            )
        if bool_chk(mythic):  # legendary
            query["$or"].append(
                {"legendary": 1}
            )
        if bool_chk(legendary):  # mythic
            query["$or"].append(  # fix it 2.21
                {"mythic": 1}
            )
        if bool_chk(original):
            query["original_id"] = 0
        if bool_chk(two_player):
            query["two_player"] = 1
        if bool_chk(silver_coins):
            query["is_silver_coins"] = 1

        if bool(is_custom_song):
            query["song_id"] = int_conv(song_id)
            query["is_official_song"] = 0
        elif int_conv(song_id) >= 1:
            query["song_id"] = int_conv(song_id) - 1
            query["is_official_song"] = 1

        if uncompleted == 1 or only_completed == 1:
            completed_levels = completed_levels[1:-1].split(",")

            if uncompleted == 1:
                index = "$nin"
            else:
                index = "$in"

            query["_id"] = {index: list(map(int_conv, completed_levels))}

        if difficulty != "-":
            query["demon"] = 0
            if difficulty == "-2":  # Демон
                query["demon"] = 1
                if demon_filter > 0:
                    query["demon_type"] = demon_filter
            elif difficulty == "-3":  # Авто
                query["auto"] = 1
            elif len(difficulty.split(",")) > 1:  # Много аргументов
                difficulty = difficulty.split(",")
                query["difficulty"] = {"$in": list(map(int_conv, difficulty))}
            else:  # Один аргумент
                query["difficulty"] = int_conv(difficulty)

        if long != "-":
            if len(long.split(",")) <= 1:  # Один аргумент
                query["length"] = int_conv(long)
            else:  # Много аргументов
                long = long.split(",")
                query["length"] = {"$in": list(map(int_conv, long))}

        match int(type_pack):
            case 0:  # Поиск
                if int_conv(search) > 0:
                    query = {"_id": int_conv(search), "is_deleted": 0, "$or": []}
                elif search != "":
                    query["name"] = {"$regex": f"^{search}.*", '$options': 'i'}

            case 1:  # Больше всего загрузок
                sort = [("downloads", DESCENDING)]

            case 3:  # Тренды
                last_week = time() - (7 * 24 * 60 * 60)
                query["upload_time"] = {"$gt": last_week}

            case 4:  # Новые уровни
                sort = [("_id", DESCENDING)]

            case 5:  # Уровни игрока
                if int_conv(search) == account_id and confirmed_account:
                    query.pop("unlisted")

                sort = [("_id", DESCENDING)]
                query["account_id"] = int_conv(search)

            case 6:  # Вкладка Featured
                sort = [("rate_time", DESCENDING)]
                query["featured"] = 1

            case 7:  # Вкладка Magic
                last_week = time() - (30 * 24 * 60 * 60)
                query["upload_time"] = {"$gt": last_week}
                query["objects"] = {"$gt": 9999}
                sort = [("_id", DESCENDING)]

            case 10:  # Вкладка Map packs
                level_ids = search.split(",")
                query = {
                    "_id": {"$in": list(map(int_conv, level_ids))},
                    "is_deleted": 0
                }

            case 11:  # Вкладка Awarded (недавно оценённые)
                sort = [("rate_time", DESCENDING)]
                query["stars"] = {"$gt": 0}

            case 12:  # Вкладка Followed
                sort = [("_id", DESCENDING)]
                account_ids = followed.split(",")
                query["account_id"] = {"$in": list(map(int_conv, account_ids))}

            case 13:  # Вкладка Friends
                sort = [("_id", DESCENDING)]
                if confirmed_account:
                    friends = list(db.friend_list.find({"_id": account_id}))
                    if bool(friends):
                        friends = friends[0]["friend_list"]
                        query["account_id"] = {"$in": friends}
                    else:
                        query["account_id"] = 0

            case 16:  # Вкладка Hall of fame
                sort = [("rate_time", DESCENDING)]
                query["epic"] = 1

            case 21:  # Хранилище Daily
                time_now = int(time())

                daily_levels = list(db.daily_level.find({
                    "timestamp": {"$lte": time_now},
                    "type_daily": 0
                }).sort([("timestamp", DESCENDING)]))[:-1]

                try:
                    daily_level_ids = [i["level_id"] for i in daily_levels]
                except IndexError:
                    return "-1"

                query["_id"] = {"$in": daily_level_ids}

            case 22:  # Хранилище Weekly
                time_now = int(time())

                daily_levels = list(db.daily_level.find({
                    "timestamp": {"$lte": time_now},
                    "type_daily": 1
                }).sort([("timestamp", DESCENDING)]))[:-1]

                try:
                    daily_level_ids = [i["level_id"] for i in daily_levels]
                except IndexError:
                    return "-1"

                query["_id"] = {"$in": daily_level_ids}

            case 23:  # Хранилище событий
                return "-1"

            case 25:  # Лист уровней
                try:
                    lvl_list = db.level_list.find({"_id": int_conv(search)})[0]

                    if lvl_list["friend_only"] == 1 and confirmed_account:
                        friend_list = db.friend_list.find_one({"_id": account_id})

                        if lvl_list["account_id"] == account_id:
                            pass
                        elif lvl_list["account_id"] not in friend_list:
                            return "-1"

                    else:
                        return "-1"
                except IndexError:
                    return "-1"

                if db.action_download.count_documents({
                    "list_id": int_conv(search), "account_id": account_id
                }) == 0:
                    db.action_download.insert_one({
                        "list_id": int_conv(search),
                        "account_id": account_id,
                        "ip": get_ip(),
                        "timestamp": int(time())
                    })

                query["_id"] = {"$in": lvl_list["levels"]}

            case 27:  # Отправленные уровни
                query["_id"] = {"$in": [i["level_id"] for i in db.suggest.find()]}

    offset = page * 10

    levels = db.level.find(query).skip(offset).limit(10)

    if sort:
        levels.sort(sort)

    if not bool(query["$or"]):
        del query["$or"]

    levels = tuple(levels)
    response = ""

    if not bool(levels):
        return "#0:0:10"

    if int(type_pack) == 0 and int_conv(search) > 0:
        if levels[0]["friend_only"] == 1:
            try:
                friend_list = db.friend_list.find_one(
                    {"_id": levels[0]["account_id"]}
                )["friend_list"]
            except IndexError:
                return "-1"

            if account_id == levels[0]["account_id"]:
                pass
            elif account_id not in friend_list:
                return "-1"

    for lvl in levels:
        diff = 0

        if lvl["difficulty"] > 0:
            diff = lvl["difficulty"] * 10
            dd = 10
        else:
            dd = 0

        if lvl["legendary"] == 1:
            lvl["epic"] = 2
        if lvl["mythic"] == 1:
            lvl["epic"] = 3

        demon = "" if lvl["demon"] == 0 else 1
        auto = "" if lvl["auto"] == 0 else 1

        official_song_id = lvl["song_id"] if lvl["is_official_song"] == 1 else 0
        non_official_song_id = lvl["song_id"] if lvl["is_official_song"] == 0 else 0

        single_response = {
            1: lvl["_id"], 2: lvl["name"], 5: lvl["version"], 6: lvl["account_id"],
            8: dd, 9: diff, 10: lvl["downloads"], 12: official_song_id, 13: gd_version,
            14: lvl["likes"], 17: demon, 43: demon_conv(lvl["demon_type"]), 25: auto,
            18: lvl["stars"], 19: lvl["featured"], 42: lvl["epic"], 45: lvl["objects"], 3: lvl["desc"],
            15: lvl["length"], 30: lvl["original_id"], 31: lvl["two_player"], 37: lvl["coins"],
            38: lvl["is_silver_coins"], 39: 0, 46: 1, 47: 2, 35: non_official_song_id, 44: gauntlet_bool
        }

        response += resp_proc(single_response) + "|"
    else:
        response = response[:-1] + "#"

    hash_string = ""
    response_user = []
    response_user_name = {}

    for lvl in levels:
        response_user.append(lvl['account_id'])
        response_user_name[lvl['account_id']] = lvl['username']

        hash_string += str(lvl["_id"])[0] + str(lvl["_id"])[-1] + \
                       str(lvl["stars"]) + str(lvl["is_silver_coins"])
    else:
        response_user = list(set(response_user))

        for user in response_user:
            response += f"{user}:{response_user_name[user]}:{user}|"

        response = response[:-1] + "#"

    for lvl in levels:
        if (lvl["song_id"] > 0 and lvl["is_official_song"] == 0) or lvl["song_ids"] != "":
            song_ids = [lvl["song_id"]]

            if lvl["song_ids"] != "":
                song_ids += list(map(int, lvl["song_ids"].split(",")))

            for song in song_ids:
                try:
                    song_info = list(db.song.find({"_id": song}))[0]
                    single_song = {
                        1: song_info["_id"], 2: song_info["name"], 3: 0,
                        4: song_info["artist_name"], 5: "{0:.2f}".format(song_info["size"]),
                        6: "", 10: song_info["link"], 7: "", 8: 0
                    }
                    response += resp_proc(single_song, 3)[:-1] + ":~"
                except IndexError:
                    continue
    else:
        if response[-2:] == ":~":
            response = response[:-2]

    response += f"#{db.level.count_documents(query)}:{offset}:10#{return_hash(hash_string)}"

    return response
