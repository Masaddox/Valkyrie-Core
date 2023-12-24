import uuid
from time import time
from . import account
from threading import Thread

from config import (
    PATH_TO_DATABASE, ACCOUNTS_ACTIVATION_VIA_MAIL,
    GD_SERVER_NAME, DOMAIN, REDIS_PREFIX
)

from utils import database as db

from utils.last_id import last_id
from utils.regex import char_clean
from utils.redis_db import client as rd
from utils.mail_sender import mail_sender
from utils.passwd import password_hashing
from utils.request_get import request_get
from utils.check_secret import check_secret


WHITELIST = True
WHITELIST_EMAILS = ["gmail.com", "ya.ru", "yandex.by", "yandex.com",
                    "yandex.kz", "yandex.ru", "mail.ru", "internet.ru",
                    "bk.ru", "inbox.ru", "list.ru"]


@account.route(f"{PATH_TO_DATABASE}/accounts/registerGJAccount.php", methods=("POST", "GET"))
def register_account():
    if not check_secret(
        request_get("secret"), 0
    ):
        return "-1"

    username = char_clean(request_get("userName"))
    password = request_get("password")
    email = request_get("email")

    if len(username) > 15 or len(password) > 20 or \
       len(email) > 32:
        return "-1"

    if WHITELIST:
        if email.split("@")[1].lower() not in WHITELIST_EMAILS:
            return "-1"

    if db.account.count_documents(
        {"$or": [
            {"username": {"$regex": f"^{username}$", '$options': 'i'}},
            {"email": {"$regex": f"^{email}$", '$options': 'i'}}
        ]}
    ) == 1:
        return "-1"

    account_id = last_id(db.account)

    if ACCOUNTS_ACTIVATION_VIA_MAIL:
        code = str(uuid.uuid4())

        message_data = {
            "title": f"Activate your account | {GD_SERVER_NAME}",
            "recipient": email,
            "body": f"Your username: {username}\nAccount activation link: {DOMAIN}/activate_account?code={code}"
        }

        sending_message = Thread(target=mail_sender, args=(message_data,))
        sending_message.start()

        rd.set(f"{REDIS_PREFIX}:{code}:confirm", account_id, 3600)

    sample_account = {
        "_id": account_id,
        "username": username,
        "password": password_hashing(password),
        "email": email,
        "discord_id": 0,
        "date": int(time()),
        "is_banned": 0,
        "is_valid": 0
    }

    db.account.insert_one(sample_account)

    return "1"
