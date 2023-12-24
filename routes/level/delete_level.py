import os
from . import level
from os.path import join
from threading import Thread
from config import PATH_TO_DATABASE, PATH_TO_ROOT

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret


def removal_of_residues(level_id):
    level_id = str(level_id)

    all_files = os.listdir(
        join(PATH_TO_ROOT, "data", "level", "old")
    )

    for file in all_files:
        if file[:len(level_id)] == level_id:
            os.remove(
                join(PATH_TO_ROOT, "data", "level", "old", file)
            )

    return


@level.route(f"{PATH_TO_DATABASE}/deleteGJLevelUser20.php", methods=("POST", "GET"))
def delete_level():
    if not check_secret(
        request_get("secret"), 2
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    level_id = request_get("levelID", "int")

    if not check_password(
        account_id, password
    ):
        return "-1"

    if db.level.count_documents({
        "_id": level_id, "delete_prohibition": 0,
        "is_deleted": 0, "stars": 0, "account_id": account_id
    }) == 0:
        return "-1"

    db.level.update_one({"_id": level_id}, {"$set": {"is_deleted": 1}})
    db.level_comment.delete_many({"level_id": level_id})

    os.remove(join(
        PATH_TO_ROOT, "data", "level", f"{str(level_id)}.level"
    ))

    th = Thread(name="removal_of_residues",
                target=removal_of_residues,
                args=(level_id,))
    th.start()

    return "1"
