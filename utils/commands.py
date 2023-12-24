import os
from time import time
from os.path import join
from config import PATH_TO_ROOT
from routes.level.delete_level import removal_of_residues

from utils import database as db
from utils.regex import char_clean


def mod_commands(account_id, level_id, command):
    role_assign = tuple(db.role_assign.find({"_id": account_id}))

    if not bool(role_assign):
        return False

    role_assign = role_assign[0]
    mod_level = db.role.find({"_id": role_assign["role_id"]})[0]["mod_level"]

    command_split = command.split(" ")

    query_level = {}

    # Moderator
    if command == "!verifycoins":
        query_level = {"is_silver_coins": 1}

    elif command == "!unverifycoins":
        query_level = {"is_silver_coins": 0}

    elif mod_level >= 2:  # Elder Moderator

        if command == "!delete":
            db.level.update_one({"_id": level_id}, {"$set": {"is_deleted": 1}})
            db.level_comment.delete_many({"level_id": level_id})

            os.remove(join(
                PATH_TO_ROOT, "data", "level", f"{str(level_id)}.level"
            ))

            removal_of_residues(level_id)

        elif command_split[0] == "!rate":
            if len(command_split) == 2:
                query_level = {
                    "difficulty": int(command_split[1]),
                }
            elif len(command_split) == 3:
                query_level = {
                    "difficulty": int(command_split[1]),
                    "stars": int(command_split[2]),
                    "rate_time": int(time())
                }

        elif command == "!unrate":
            query_level = {
                "difficulty": 0,
                "stars": 0,
                "featured": 0,
                "epic": 0,
                "is_silver_coins": 0,
                "auto": 0,
                "demon": 0,
                "demon_type": 0,
                "rate_time": 0
            }

        elif command == "!featured":
            query_level = {"featured": 1}

        elif command == "!unfeatured":
            query_level = {"featured": 0}

        elif command == "!epic":
            query_level = {"epic": 1, "featured": 1}

        elif command == "!unepic":
            query_level = {"epic": 0}

        elif command == "!demon":
            query_level = {
                "demon": 1,
                "stars": 10,
                "difficulty": 5,
                "demon_type": 3
            }

        elif command == "!undemon":
            query_level = {
                "demon": 0,
                "stars": 0,
                "demon_type": 0
            }

        elif command_split[0] == "!song":
            if len(command_split) != 3:
                return False

            if command_split[1] == "custom":
                query_level = {"is_official_song": 0}
            elif command_split[1] == "official":
                query_level = {"is_official_song": 1}

            query_level.update({
                "song_id": int(command_split[2])
            })

        elif command_split[0] == "!rename":
            if len(command_split) == 1:
                return False

            level_name = ""

            for i in range(len(command_split) - 1):
                level_name += command_split[i + 1] + " "

            if len(level_name[:-1]) > 20:
                return False

            query_level = {"name": char_clean(level_name[:-1])}

        elif command_split[0] == "!setacc":
            if len(command_split) == 1:
                return False

            try:
                user_info = db.account_stat.find({
                    "username": {"$regex": f"^{char_clean(command_split[1])}$", '$options': 'i'}
                })[0]
            except:
                return False

            query_level = {
                "account_id": user_info["_id"],
                "username": user_info["username"]
            }

        elif command_split[0] == "!pass":
            if len(command_split) == 1:
                return False

            query_level = {"password": int(command_split[1])}

    if bool(query_level):
        db.level.update_one({"_id": level_id}, {"$set": query_level})

    return True
