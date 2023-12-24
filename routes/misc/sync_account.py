from . import misc
from os.path import join
from config import PATH_TO_ROOT

from utils import database as db

from utils.regex import char_clean
from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret


@misc.route("/database/accounts/syncGJAccountNew.php", methods=("POST", "GET"))
def sync_account():
    if not check_secret(
        request_get("secret"), 0
    ):
        return "-1"

    username = char_clean(request_get("userName"))
    password = request_get("password")

    try:
        account_id = db.account_stat.find_one(
            {"username": {"$regex": f"^{username}$", '$options': 'i'}})["_id"]
    except TypeError:
        return "-1"
    except KeyError:
        return "-1"

    if not check_password(
        account_id, password, is_gjp=False, fast_mode=False
    ):
        return "-1"

    try:
        with open(join(
            PATH_TO_ROOT, "data", "account", f"{account_id}.account"
        ), "r") as file:
            save_data = file.read()
    except FileNotFoundError:
        return "-1"

    return save_data + ";21;30;a;a"
