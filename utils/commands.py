import os
from time import time
from os.path import join
from config import PATH_TO_ROOT, COMMAND_PREFIX
from routes.level.delete_level import removal_of_residues

from utils import database as db
from utils.regex import char_clean


def commands(account_id, level_id, command):
    role_assign_tuple = tuple(db.role_assign.find({"_id": account_id}))

    is_mod = False

    if len(role_assign_tuple) == 0:
        return False  # Заглушка
    else:
        is_mod = True
        role_assign = role_assign_tuple[0]

    command = command[len(COMMAND_PREFIX):]
    command_split = command.split(" ")

    query_level = {}

    match command_split[0]:
        case "veritycoins":
            if is_mod and role_assign["command_access"]["veritycoins"]:

                try:
                    vercoins = int(command_split[1])
                except IndexError:
                    vercoins = 1

                query_level = {
                    "is_silver_coins": vercoins if 0 <= vercoins <= 1 else 0
                }

        case "unveritycoins":
            if is_mod and role_assign["command_access"]["veritycoins"]:
                query_level = {
                    "is_silver_coins": 0
                }

        case "delete":
            if is_mod and role_assign["command_access"]["delete"]:
                db.level.update_one({"_id": level_id}, {"$set": {"is_deleted": 1}})
                return True

        case "fulldelete":
            if is_mod and role_assign["command_access"]["delete"]:
                db.level.update_one({"_id": level_id}, {"$set": {"is_deleted": 1}})

                os.remove(join(
                    PATH_TO_ROOT, "data", "level", f"{str(level_id)}.level"
                ))

                removal_of_residues(level_id)
                return True

        case "rate":
            if is_mod and role_assign["command_access"]["rate"]:
                diff = 0

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
                        stars = int(command_split[2])
                        query_level = {
                            "difficulty": diff if 0 <= diff <= 10 else 0,
                            "stars": stars if 0 <= stars <= 10 else 0,
                            "rate_time": int(time())
                        }
                    case _:
                        return False

        case "unrate":
            if is_mod and role_assign["command_access"]["rate"]:
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

        case "stars":
            if is_mod and role_assign["command_access"]["stars"]:

                try:
                    stars = int(command_split[1])
                except IndexError:
                    stars = 0

                query_level = {
                    "stars": stars if 0 <= stars <= 10 else 0
                }

        case "unstars":
            if is_mod and role_assign["command_access"]["stars"]:
                query_level = {
                    "stars": 0
                }

        case "featured":
            if is_mod and role_assign["command_access"]["featured"]:

                try:
                    feat = int(command_split[1])
                except IndexError:
                    feat = 1

                query_level = {
                    "featured": feat if 0 <= feat <= 1 else 0
                }

        case "unfeatured":
            if is_mod and role_assign["command_access"]["featured"]:
                query_level = {
                    "featured": 0
                }

        case "epic":
            if is_mod and role_assign["command_access"]["epic"]:

                try:
                    epic = int(command_split[1])
                except IndexError:
                    epic = 1

                query_level = {
                    "featured": 1,
                    "epic": epic if 0 <= epic <= 1 else 0
                }

        case "unepic":
            if is_mod and role_assign["command_access"]["epic"]:
                query_level = {
                    "epic": 0
                }

        case "legendary":
            if is_mod and role_assign["command_access"]["legendary"]:

                try:
                    legend = int(command_split[1])
                except IndexError:
                    legend = 1

                query_level = {
                    "featured": 1,
                    "epic": 0,
                    "legendary": legend if 0 <= legend <= 1 else 0
                }

        case "unlegendary":
            if is_mod and role_assign["command_access"]["legendary"]:
                query_level = {
                    "legendary": 0
                }

        case "mythic":
            if is_mod and role_assign["command_access"]["mythic"]:

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
            if is_mod and role_assign["command_access"]["mythic"]:
                query_level = {
                    "mythic": 0
                }

        case "demon":
            if is_mod and role_assign["command_access"]["demon"]:
                if len(command_split) == 2:
                    demon = int(command_split[1])
                else:
                    demon = 3

                query_level = {
                    "demon": 1,
                    "stars": 10,
                    "difficulty": 5,
                    "demon_type": demon,
                    "rate_time": int(time())
                }

        case "undemon":
            if is_mod and role_assign["command_access"]["demon"]:
                query_level = {
                    "demon": 0,
                    "stars": 9,
                    "demon_type": 0
                }

        case "song":
            if len(command_split) != 3:
                return False

            if is_mod and role_assign["command_access"]["song"]:

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
            if is_mod and role_assign["command_access"]["pass"]:
                password = 0

                if len(command_split) == 2:
                    try:
                        password = int(command_split[1]) if 0 <= int(command_split[1]) <= 999_999 else 0
                    except ValueError:
                        password = 0 if command_split[1] == "close" else 1 if command_split[1] == "open" else 0

                query_level = {
                    "password": password if len(str(password)) == 1 else int("1" + str(password))
                }

        case "rename":
            if is_mod and db.level.count_documents({"_id": level_id, "account_id": account_id}) == 0:
                if len(command_split) == 1:
                    return False

                level_name = ""

                for i in range(len(command_split) - 1):
                    level_name += command_split[i + 1] + " "

                if len(level_name[:-1]) > 20:
                    return False

                query_level = {"name": char_clean(level_name[:-1])}

        case "setacc":
            if len(command_split) == 1:
                return False

            if is_mod and role_assign["command_access"]["setacc"]:
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
            if len(command_split) == 1:
                return False

            if is_mod and role_assign["command_access"]["unlisted"]:
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

        case "daily":
            pass

        case "weekly":
            pass

    if bool(query_level):
        db.level.update_one({"_id": level_id}, {"$set": query_level})

    return True
