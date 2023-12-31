import os
from time import time
from os.path import join

from icecream import ic
from pymongo import DESCENDING
from datetime import datetime, timedelta
from config import PATH_TO_ROOT, COMMAND_PREFIX
from routes.level.delete_level import removal_of_residues

from utils import database as db
from utils.last_id import last_id
from utils.regex import char_clean


def commands(account_id, level_id, command, is_level):
    role_assign = tuple(db.role_assign.find({"_id": account_id}))
    is_mod = False

    if len(role_assign) == 0:
        return False  # Заглушка
    else:
        is_mod = True
        role = db.role.find({"_id": role_assign[0]["role_id"]})[0]

    command = command[len(COMMAND_PREFIX):]
    command_split = command.split(" ")

    coll = db.level
    query_level = {}

    match command_split[0]:
        case "veritycoins":
            if not is_mod or not role["command_access"]["veritycoins"]:
                return False

            try:
                vercoins = int(command_split[1])
            except IndexError:
                vercoins = 1

            query_level = {
                "is_silver_coins": vercoins if 0 <= vercoins <= 1 else 0
            }

        case "unveritycoins":
            if not is_mod or not role["command_access"]["veritycoins"]:
                return False

            query_level = {
                "is_silver_coins": 0
            }

        case "delete":
            if not is_mod or not role["command_access"]["delete"]:
                return False

            db.level.update_one({"_id": level_id}, {"$set": {"is_deleted": 1}})
            return True

        case "fulldelete":
            if not is_mod or not role["command_access"]["delete"]:
                return False

            db.level.update_one({"_id": level_id}, {"$set": {"is_deleted": 1}})

            os.remove(join(
                PATH_TO_ROOT, "data", "level", f"{str(level_id)}.level"
            ))

            removal_of_residues(level_id)
            return True

        case "deletesend":
            if not is_mod or not role["command_access"]["delete"]:
                return False

            if db.suggest.count_documents({
                "level_id": level_id
            }) == 0:
                return False

            db.suggest.delete_one({
                "level_id": level_id
            })

            return True

        case "rate":
            if not is_mod or not role["command_access"]["rate"]:
                return False

            match len(command_split):
                case 1:
                    query_level = {
                        "difficulty": 0
                    }
                case 2:
                    diff = int(command_split[1])
                    query_level = {
                        "difficulty": diff if 0 <= diff <= 10 else 0
                    }
                case 3:
                    diff = int(command_split[1])
                    stars = int(command_split[2])
                    query_level = {
                        "difficulty": diff if 0 <= diff <= 10 else 0,
                        "stars": stars if 0 <= stars <= 10 else 0,
                        "rate_time": int(time()) if stars > 0 else 0
                    }
                case _:
                    return False

        case "unrate":
            if not is_mod or not role["command_access"]["rate"]:
                return False

            query_level = {
                "difficulty": 0,
                "stars": 0,
                "featured": 0,
                "epic": 0,
                "legendary": 0,
                "mythic": 0,
                "is_silver_coins": 0,
                "auto": 0,
                "demon": 0,
                "demon_type": 0,
                "rate_time": 0
            }

        case "ratelist":
            if not is_mod or not role["command_access"]["rate"]:
                return False

            if is_level:
                return False

            coll = db.level_list

            match len(command_split):
                case 1:
                    query_level = {
                        "difficulty": -1
                    }
                case 2:
                    diff = int(command_split[1])
                    query_level = {
                        "difficulty": diff if -1 <= diff <= 10 else 0
                    }
                case 3:
                    diff = int(command_split[1])
                    diamonds = int(command_split[2])
                    query_level = {
                        "difficulty": diff if -1 <= diff <= 10 else 0,
                        "diamonds": diamonds if 0 <= diamonds <= 10 else 0,
                        "count_for_reward": 1,
                        "rate_time": int(time()) if diamonds > 0 else 0
                    }
                case _:
                    return False

        case "unratelist":
            if not is_mod or not role["command_access"]["rate"]:
                return False

            if is_level:
                return False

            query_level = {
                "diamonds": 0,
                "featured": 0,
                "count_for_reward": 0,
                "rate_time": 0
            }

        case "cfr":  # count for reward
            if not is_mod or not role["command_access"]["rate"]:
                return False

            if is_level:
                return False

            try:
                count_for_reward = int(command_split[1])
            except IndexError:
                count_for_reward = 0
            except ValueError:
                count_for_reward = 0

            query_level = {
                "count_for_reward": count_for_reward
            }

        case "stars":
            if not is_mod or not role["command_access"]["stars"]:
                return False

            try:
                stars = int(command_split[1])
            except IndexError:
                stars = 0

            query_level = {
                "stars": stars if 0 <= stars <= 10 else 0
            }

            if stars == 0:
                query_level["rate_time"] = 0

        case "unstars":
            if not is_mod or not role["command_access"]["stars"]:
                return False

            query_level = {
                "stars": 0,
                "rate_time": 0
            }

        case "featured":
            if not is_mod or not role["command_access"]["featured"]:
                return False

            if not is_level:
                coll = db.level_list

            try:
                feat = int(command_split[1])
            except IndexError:
                feat = 1

            query_level = {
                "featured": feat if 0 <= feat <= 1 else 0
            }

        case "unfeatured":
            if not is_mod or not role["command_access"]["featured"]:
                return False

            if not is_level:
                coll = db.level_list

            query_level = {
                "featured": 0
            }

        case "epic":
            if not is_mod or not role["command_access"]["epic"]:
                return False

            try:
                epic = int(command_split[1])
            except IndexError:
                epic = 1

            query_level = {
                "featured": 1,
                "epic": epic if 0 <= epic <= 1 else 0,
                "legendary": 0,
                "mythic": 0
            }

        case "unepic":
            if not is_mod or not role["command_access"]["epic"]:
                return False

            query_level = {
                "epic": 0
            }

        case "legendary":
            if not is_mod or not role["command_access"]["legendary"]:
                return False

            try:
                legend = int(command_split[1])
            except IndexError:
                legend = 1

            query_level = {
                "featured": 1,
                "epic": 0,
                "legendary": legend if 0 <= legend <= 1 else 0,
                "mythic": 0
            }

        case "unlegendary":
            if not is_mod or not role["command_access"]["legendary"]:
                return False

            query_level = {
                "legendary": 0
            }

        case "mythic":
            if not is_mod or not role["command_access"]["mythic"]:
                return False

            try:
                mythic = int(command_split[1])
            except IndexError:
                mythic = 1

            query_level = {
                "featured": 1,
                "epic": 0,
                "legendary": 0,
                "mythic": mythic if 0 <= mythic <= 1 else 0
            }

        case "unmythic":
            if not is_mod or not role["command_access"]["mythic"]:
                return False

            query_level = {
                "mythic": 0
            }

        case "demon":
            if not is_mod or not role["command_access"]["demon"]:
                return False

            if len(command_split) == 2:
                demon = int(command_split[1])

            else:
                demon = 3

            if demon == 0:  # undemon
                query_level = {
                    "demon": 0,
                    "stars": 9,
                    "demon_type": 0
                }
            else:
                query_level = {
                    "demon": 1,
                    "stars": 10,
                    "difficulty": 5,
                    "demon_type": demon,
                    "rate_time": int(time())
                }

        case "undemon":
            if not is_mod or not role["command_access"]["demon"]:
                return False

            query_level = {
                "demon": 0,
                "stars": 9,
                "demon_type": 0
            }

        case "song":
            if not is_mod or not role["command_access"]["song"]:
                return False

            if len(command_split) != 3:
                return False

            match command_split[1]:
                case "c":
                    query_level = {"is_official_song": 0}
                case "custom":
                    query_level = {"is_official_song": 0}

                case "o":
                    query_level = {"is_official_song": 1}
                case "official":
                    query_level = {"is_official_song": 1}

                case _:
                    return False

            if query_level["is_official_song"] == 0:
                if db.song.count_documents({
                    "_id": int(command_split[2])
                }) == 0:
                    return False

            query_level.update({
                "song_id": int(command_split[2])
            })

        case "pass":
            if not is_mod or not role["command_access"]["pass"]:
                return False

            password = 0

            if len(command_split) == 2:
                try:
                    password = int(command_split[1]) if 0 <= int(command_split[1]) <= 999_999 else 0
                except ValueError:
                    password = 0 if command_split[1] == "close" else 1 if command_split[1] == "open" else 0

            if len(str(password)) == 1:
                password = 0 if password == 0 else 1
            elif len(str(password)) >= 2:
                number_zero = 6 - len(str(password))
                password = int("1" + f"{"0" * number_zero}" + str(password))

            query_level = {
                "password": password
            }

        case "rename":
            if not is_mod or not role["command_access"]["rename"]:
                return False

            if len(command_split) == 1:
                return False

            level_name = ""

            for i in range(len(command_split) - 1):
                level_name += command_split[i + 1] + " "

            if len(level_name[:-1]) > 20:
                return False

            query_level = {"name": char_clean(level_name[:-1])}

        case "setacc":
            if not is_mod or not role["command_access"]["setacc"]:
                return False

            if len(command_split) == 1:
                return False

            try:
                user_info = db.account_stat.find({
                    "username": {"$regex": f"^{char_clean(command_split[1])}$", '$options': 'i'}
                })[0]
            except IndexError:
                return False

            query_level = {
                "account_id": user_info["_id"],
                "username": user_info["username"]
            }

        case "unlisted":
            if not is_mod or not role["command_access"]["unlisted"]:
                return False

            if len(command_split) == 1:
                return False

            unlisted = 0
            friend_only = 0

            match len(command_split):
                case 2:
                    unlisted = 1 if int(command_split[1]) >= 1 else 0
                case 3:
                    unlisted = 1 if int(command_split[2]) >= 1 else 0
                    if command_split[1] == "friend":
                        friend_only = 1

            query_level = {
                "unlisted": unlisted,
                "friend_only": friend_only
            }

        case "auto":
            if not is_mod or not role["command_access"]["auto"]:
                return False

            try:
                auto = int(command_split[1])
            except IndexError:
                auto = 1

            query_level = {
                "auto": auto,
                "difficulty": auto
            }

        case "unauto":
            if not is_mod or not role["command_access"]["auto"]:
                return False

            query_level = {
                "auto": 0,
                "difficulty": 0
            }

        case "daily":
            if not is_mod or not role["command_access"]["daily"]:
                return False

            time_limit = 86400

            today = datetime.now().date()
            midnight = datetime.combine(today, datetime.min.time()).timestamp()

            time_now = int(time())

            last_daily_level = list(db.daily_level.find(
                {"type_daily": 0}
            ).sort("timestamp", DESCENDING).limit(1))

            if len(last_daily_level) > 0:
                if last_daily_level[0]["timestamp"] + time_limit <= time_now:
                    timestamp = midnight
                else:
                    timestamp = last_daily_level[0]["timestamp"] + time_limit
            else:
                timestamp = midnight

            db.daily_level.insert_one({
                "daily_id": last_id(db.daily_level, "daily_id"),
                "type_daily": 0,
                "level_id": level_id,
                "timestamp": timestamp
            })

        case "weekly":
            if not is_mod or not role["command_access"]["weekly"]:
                return False

            time_limit = 604800

            today = datetime.now()
            days_since_monday = (today.weekday() - 0) % 7
            midnight_today = datetime.combine(today.date(), datetime.min.time())
            midnight_last_monday = midnight_today - timedelta(days=days_since_monday)
            midnight_last_monday = int(midnight_last_monday.timestamp())

            time_now = int(time())

            last_daily_level = list(db.daily_level.find(
                {"type_daily": 1}
            ).sort("timestamp", DESCENDING).limit(1))

            if len(last_daily_level) > 0:
                if last_daily_level[0]["timestamp"] + time_limit * 2 <= time_now:
                    timestamp = midnight_last_monday
                else:
                    timestamp = last_daily_level[0]["timestamp"] + time_limit
            else:
                timestamp = midnight_last_monday

            db.daily_level.insert_one({
                "daily_id": last_id(db.daily_level, "daily_id"),
                "type_daily": 1,
                "level_id": level_id,
                "timestamp": timestamp
            })

    if bool(query_level):
        coll.update_one({"_id": level_id}, {"$set": query_level})

    return True
