from . import account
from config import PATH_TO_DATABASE, REDIS_PREFIX

from utils import database as db

from utils.regex import char_clean
from utils.passwd import check_password
from utils.redis_db import client as rd
from utils.check_secret import check_secret
from utils.request_get import request_get, get_ip


LOGIN_ATTEMPTS_TIMELINE = 3600


@account.route(f"{PATH_TO_DATABASE}/accounts/loginGJAccount.php", methods=("POST", "GET"))
def login_account():
    ip = get_ip()
    login_attempts = rd.get(f"{REDIS_PREFIX}:{ip}:login")

    if login_attempts is not None:
        login_attempts = int(login_attempts.decode())
        if login_attempts >= 8:
            return "-12"

    if not check_secret(
        request_get("secret"), 0
    ):
        return "-1"

    username = char_clean(request_get("userName"))
    password = request_get("password")

    if len(username) > 15 or len(password) > 20:
        return "-1"

    try:
        account_id = db.account.find_one(
            {"username": {"$regex": f"^{username}$", '$options': 'i'}})["_id"]

        if not check_password(
            account_id, password, is_gjp=False, fast_mode=False
        ):
            raise
    except:
        if login_attempts is None:
            rd.set(f"{REDIS_PREFIX}:{ip}:login", 0, LOGIN_ATTEMPTS_TIMELINE)

        rd.incr(f"{REDIS_PREFIX}:{ip}:login", 1)
        return "-1"

    return f"{account_id},{account_id}"
