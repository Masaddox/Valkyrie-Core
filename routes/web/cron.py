import logging
from . import web
from time import time
from os.path import join
from config import REDIS_PREFIX, PATH_TO_ROOT
from routes.score.get_scores import upload_scores

from utils import database as db

from utils.redis_db import client as rd
from utils.limit_check import limit_check


CP_RATE = 1
CP_FEATURED = 2
CP_EPIC = 4
CP_LEGENDARY = 6
CP_MYTHIC = 10


@web.route("/cron/<task>/<key>", methods=("POST", "GET"))
def cron(task, key):
    if db.master_key.count_documents({
        "key": key,
        "comment": "for cron"
    }) == 0:
        return ""

    if task == "gd":

        logging.basicConfig(
            level=logging.INFO,
            filename=join(PATH_TO_ROOT, "data", "log", f"{int(time())}_cron_gd.log"),
            filemode="w"
        )

        """ Выдача creator points """

        creator_list = {}
        levels = tuple(db.level.find({"stars": {"$gt": 0}}))

        for creator in db.account_stat.find({"creator_points": {"$gt": 0}}):
            creator_list[creator["_id"]] = 0

        if len(levels) != 0:
            for lvl in levels:
                if lvl["account_id"] not in creator_list:
                    creator_list[lvl["account_id"]] = 0

                if (lvl["featured"] == 0 and lvl["epic"] == 0
                        and lvl["legendary"] == 0 and lvl["mythic"] == 0):
                    creator_list[lvl["account_id"]] += CP_RATE

                elif (lvl["featured"] == 1 and lvl["epic"] == 0
                        and lvl["legendary"] == 0 and lvl["mythic"] == 0):
                    creator_list[lvl["account_id"]] += CP_FEATURED

                elif lvl["epic"] == 1 and lvl["legendary"] == 0 and lvl["mythic"] == 0:
                    creator_list[lvl["account_id"]] += CP_EPIC

                elif lvl["legendary"] == 1 and lvl["mythic"] == 0:
                    creator_list[lvl["account_id"]] += CP_LEGENDARY

                elif lvl["mythic"] == 1:
                    creator_list[lvl["account_id"]] += CP_MYTHIC

            for creator in creator_list:
                logging.info(f"{creator} - {creator_list[creator]} CP")

                db.account_stat.update_one({"_id": creator}, {"$set": {
                    "creator_points": creator_list[creator]
                }})

        upload_scores("creators")

        del creator_list

        """ Античит """

        max_stars = 202  # Сколько можно собрать статистику, не проходя онлайн уровней
        max_moons = 25
        max_demons = 3
        max_gold_coins = 81
        max_silver_coins = 0

        users = tuple(db.account_stat.find({"is_top_banned": 0}))
        map_packs = tuple(db.map_pack.find())
        gauntlets = tuple(db.gauntlet.find())
        daily_levels = tuple(db.daily_level.find())

        for level in levels:
            if level["length"] == 5:
                max_moons += level["stars"]
            else:
                max_stars += level["stars"]
            max_demons += level["demon"]
            max_silver_coins += level["coins"] if level["is_silver_coins"] == 1 else 0

        if bool(map_packs):
            for map_pack in map_packs:
                max_stars += map_pack["stars"]
                max_gold_coins += map_pack["coins"]

        if bool(gauntlets):
            for gauntlet in gauntlets:
                level_ids = gauntlet["levels"].split(",")
                for level_id in level_ids:
                    try:
                        level = db.level.find({"_id": int(level_id)})[0]
                    except IndexError:
                        continue

                    if level["length"] == 5:
                        max_moons += level["stars"]
                    else:
                        max_stars += level["stars"]

                    max_demons += level["demon"]
                    max_silver_coins += level["coins"] if level["is_silver_coins"] == 1 else 0

        if bool(daily_levels):
            for daily_level in daily_levels:
                level_id = daily_level["level_id"]
                level = db.level.find({"_id": int(level_id)})[0]

                if level["length"] == 5:
                    max_moons += level["stars"]
                else:
                    max_stars += level["stars"]

                max_demons += level["demon"]
                max_silver_coins += level["coins"] if level["is_silver_coins"] == 1 else 0

        logging.info(
            f"stars - {max_stars}; moons - {max_moons}; demons - {max_demons}; "
            f"gold_coins - {max_gold_coins}; silver_coins - {max_silver_coins}"
        )

        for user in users:
            if not limit_check(
                (user["stars"], max_stars), (user["moons"], max_moons), (user["demons"], max_demons),
                (user["user_coins"], max_silver_coins), (user["secret_coins"], max_gold_coins)
            ):
                logging.info(f"{user["_id"]} BANNED!")
                db.account_stat.update_one({"_id": user["_id"]}, {"$set": {
                    "is_top_banned": 1
                }})

        """ Обновление поля global_rank у игроков """

        top_list = rd.get(f"{REDIS_PREFIX}:top:top")

        if top_list is None:
            top_list = upload_scores()

        top_list = top_list.split("|")

        for i in range(1, len(top_list)):
            user = top_list[i - 1].split(":")

            db.account_stat.update_one({"_id": int(user[3])}, {"$set": {
                "global_rank": i
            }})

        """ Очистка неактивированных аккаунтов """

        db.account.delete_many({
            "is_valid": 0,
            "date": {"$lte": int(time()) - 3600}  # Есть только час на активацию
        })

        """ Если игрок лишился статуса модератора """

        for user in db.account_stat.find({"mod_badge": {"$gt": 0}}):
            if db.role_assign.count_documents({"_id": user["_id"]}) == 0:
                comment_color = user["comment_color"] if user["vip_status"] == 1 else ""
                prefix = user["prefix"] if user["prefix"] not in ("Moderator", "Elder Moderator") else ""

                db.account_stat.update_one({"_id": user["_id"]}, {"$set": {
                    "mod_badge": 0,
                    "prefix": prefix,
                    "comment_color": comment_color
                }})

        logging.shutdown()
        return "1"

    else:
        return ""
