from . import misc
from os.path import join
from sys import getsizeof
from icecream import ic
from config import PATH_TO_ROOT, REDIS_PREFIX

from utils import database as db

from utils.regex import char_clean
from utils.redis_db import client as rd
from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret


MAX_SIZE = [  # no vip, vip
    20 * 1024 * 1024,
    50 * 1024 * 1024
]


@misc.route("/database/accounts/backupGJAccountNew.php", methods=("POST", "GET"))
def backup_account():
    if not check_secret(
        request_get("secret"), 0
    ):
        ic()
        return "-1"

    username = char_clean(request_get("userName"))
    password = request_get("password")

    account_id = request_get("accountID", "int")
    is_gjp2 = False

    if request_get("gjp2") != "":
        is_gjp2 = True
        password = request_get("gjp2")

    if account_id <= 0:
        try:
            account_id = db.account_stat.find_one(
                {"username": {"$regex": f"^{username}$", '$options': 'i'}})["_id"]
        except TypeError:
            return "-1"
        except KeyError:
            return "-1"

    if not check_password(
        account_id, password, fast_mode=False,
        is_gjp=False, is_gjp2=is_gjp2
    ):
        return "-1"

    if rd.get(f"{REDIS_PREFIX}:{account_id}:backup") == "1":  # Проверка на тайм аут
        return "-1"

    save_data = request_get("saveData")

    vip_status = db.account_stat.find_one({"_id": account_id})["vip_status"]

    if getsizeof(save_data) > MAX_SIZE[vip_status]:
        return "-1"

    with open(join(
        PATH_TO_ROOT, "data", "account", f"{account_id}.account"
    ), "w") as file:
        file.write(save_data)

    rd.set(f"{REDIS_PREFIX}:{account_id}:backup", "1", 60)  # Тайм аут 60 секунд

    return "1"
