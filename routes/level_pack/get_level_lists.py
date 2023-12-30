from time import time
from . import level_pack
from pymongo import DESCENDING
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.response_processing import resp_proc


def int_conv(x):
    try:
        return int(x)
    except TypeError:
        return -1
    except ValueError:
        return -1


@level_pack.route(f"{PATH_TO_DATABASE}/getGJLevelLists.php", methods=("POST", "GET"))
def get_level_lists():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-100"

    account_id = request_get("accountID", "int")
    password = request_get("gjp2")

    confirmed_account = False

    if check_password(
        account_id, password,
        is_gjp=False, is_gjp2=True
    ):
        confirmed_account = True

    difficulty = request_get("diff")
    type_search = request_get("type", "int")
    demon_filter = request_get("demonFilter", "int")

    search = request_get("str")
    page = request_get("page", "int")
    followed = request_get("followed", "list_int")

    diamonds = request_get("star", "int")
    featured = request_get("featured", "int")

    query = {
        "unlisted": 0, "is_deleted": 0
    }
    sort = [("likes", DESCENDING)]

    if diamonds != 0:
        query["diamonds"] = {"$gt": 0}
    if featured != 0:
        query["featured"] = 1

    match difficulty:
        case "-1":
            query["difficulty"] = -1

        case "-2":
            query["difficulty"] = 5 + demon_filter

        case "-3":
            query["difficulty"] = 0

        case "-":
            pass

        case _:
            if difficulty != "":
                query["difficulty"] = int_conv(difficulty)

    match type_search:
        case 0:
            if int_conv(search) > 0:
                query = {"_id": int_conv(search), "is_deleted": 0}
            elif search != "":
                query["name"] = {"$regex": f"^{search}.*", '$options': 'i'}

        case 1:  # Больше всего загрузок
            sort = [("downloads", DESCENDING)]

        case 3:  # Тренды
            last_week = time() - (7 * 24 * 60 * 60)
            query["upload_time"] = {"$gt": last_week}

        case 4:  # Новые листы
            sort = [("_id", DESCENDING)]

        case 5:  # Уровни игрока
            if int_conv(search) == account_id and confirmed_account:
                query.pop("unlisted")

            sort = [("_id", DESCENDING)]
            query["account_id"] = int_conv(search)

        case 6:  # Листы (кнопка в меню, на подобии Featured)
            query["diamonds"] = {"$gt": 0}
            query["featured"] = 1

        case 7:  # Magic (что суда вставлять?)
            pass

        case 11:  # Awarded (недавно оценённые)
            query["diamonds"] = {"$gt": 0}
            sort = [("rate_time", DESCENDING)]

        case 12:  # Followed
            query["account_id"] = {"$in": followed}
            sort = [("_id", DESCENDING)]

        case 13:  # Friends
            try:
                friend_list = db.friend_list.find_one({"_id": account_id})["friend_list"]
            except IndexError:
                return "-1"

            query["account_id"] = {"$in": friend_list}
            sort = [("_id", DESCENDING)]

        case 27:  # Sent
            pass

    offset = page * 10

    level_lists = db.level_list.find(query).skip(offset).limit(10)

    if sort:
        level_lists.sort(sort)

    level_lists = tuple(level_lists)
    response = ""

    response_users = []
    response_user_names = {}

    if not bool(level_lists):
        return "#0:0:10"

    if int(type_search) == 0 and int_conv(search) > 0:
        if level_lists[0]["friend_only"] == 1:
            try:
                friend_list = db.friend_list.find_one(
                    {"_id": level_lists[0]["account_id"]}
                )["friend_list"]
            except IndexError:
                return "-1"

            if account_id == level_lists[0]["account_id"]:
                pass
            elif account_id not in friend_list:
                return "-1"

    for lvl in level_lists:
        levels = ",".join(list(map(str, lvl["levels"])))

        single_response = {
            1: lvl["_id"], 2: lvl["name"], 3: lvl["desc"], 5: lvl["version"],
            49: lvl["account_id"], 50: lvl["username"], 10: lvl["downloads"],
            7: lvl["difficulty"], 14: lvl["likes"], 19: lvl["featured"],
            51: levels, 55: lvl["diamonds"], 56: lvl["count_for_reward"],
            28: lvl["upload_time"], 29: ["update_time"]
        }

        response_users.append(lvl["account_id"])
        response_user_names[lvl["account_id"]] = lvl["username"]

        response += resp_proc(single_response) + "|"
    else:
        response = response[:-1] + "#"

    response_users = list(set(response_users))

    for user in response_users:
        response += f"{user}:{response_user_names[user]}:{user}|"
    else:
        response = response[:-1] + "#"

    response += f"{db.level_list.count_documents(query)}:{offset}:10#"
    response += "vcorevcorevcorevcorevcorevcorevcorevcore"

    return response
