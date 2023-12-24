from . import web
from time import time
from config import REDIS_PREFIX
from routes.score.get_scores import upload_scores

from utils import database as db

from utils.redis_db import client as rd
from utils.limit_check import limit_check


@web.route("/cron/<task>/<key>", methods=("POST", "GET"))
def cron(task, key):
    if db.master_key.count_documents({
        "key": key,
        "comment": "for cron"
    }) == 0:
        return ""

    if task == "gd":

        """ Константы """

        CP_RATE = 1
        CP_FEATURED = 2
        CP_EPIC = 4

        """ Выдача creator points """

        creator_list = {}
        levels = tuple(db.level.find({"stars": {"$gt": 0}}))

        for creator in db.account_stat.find({"creator_points": {"$gt": 0}}):
            creator_list[creator["_id"]] = 0

        if len(levels) != 0:
            for lvl in levels:
                if lvl["account_id"] not in creator_list:
                    creator_list[lvl["account_id"]] = 0

                if lvl["featured"] == 0 and lvl["epic"] == 0:
                    creator_list[lvl["account_id"]] += CP_RATE
                elif lvl["featured"] == 1 and lvl["epic"] == 0:
                    creator_list[lvl["account_id"]] += CP_FEATURED
                if lvl["epic"] == 1:
                    creator_list[lvl["account_id"]] += CP_EPIC

            for creator in creator_list:
                db.account_stat.update_one({"_id": creator}, {"$set": {
                    "creator_points": creator_list[creator]
                }})

        upload_scores("creators")

        del creator_list

        """ Античит """

        max_stars = 190  # Сколько можно собрать статистику, не проходя онлайн уровней
        max_demons = 3
        max_gold_coins = 66
        max_silver_coins = 0

        users = tuple(db.account_stat.find({"is_top_banned": 0}))
        map_packs = tuple(db.map_pack.find())
        gauntlets = tuple(db.gauntlet.find())
        daily_levels = tuple(db.daily_level.find())

        for level in levels:
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
                    level = db.level.find({"_id": int(level_id)})[0]

                    max_stars += level["stars"]
                    max_demons += level["demon"]
                    max_silver_coins += level["coins"] if level["is_silver_coins"] == 1 else 0

        if bool(daily_levels):
            for daily_level in daily_levels:
                level_id = daily_level["level_id"]
                level = db.level.find({"_id": int(level_id)})[0]

                max_stars += level["stars"]
                max_demons += level["demon"]
                max_silver_coins += level["coins"] if level["is_silver_coins"] == 1 else 0

        for user in users:
            if not limit_check(
                (user["stars"], max_stars), (user["demons"], max_demons),
                (user["user_coins"], max_silver_coins), (user["secret_coins"], max_gold_coins)
            ):
                db.account_stat.update_one({"_id": user["_id"]}, {"$set": {
                    "is_top_banned": 1
                }})

        """ Обновление поля global_rank у игроков """

        top_list = rd.get(f"{REDIS_PREFIX}:top:top")

        if top_list is None:
            top_list = upload_scores()
        else:
            top_list = top_list.decode()

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

        for user in db.account_stat.find({"mod_level": {"$gt": 0}}):
            if db.role_assign.count_documents({"_id": user["_id"]}) == 0:
                comment_color = user["comment_color"] if user["vip_status"] == 1 else ""
                prefix = user["prefix"] if user["prefix"] not in ("Moderator", "Elder Moderator") else ""

                db.account_stat.update_one({"_id": user["_id"]}, {"$set": {
                    "mod_level": 0,
                    "prefix": prefix,
                    "comment_color": comment_color
                }})

        return "1"

    else:
        return ""
