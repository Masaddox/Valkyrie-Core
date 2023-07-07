import uuid
from time import time
from . import account
from threading import Thread
from utils import check_secret, mail_sender, regex, last_id, passwd, \
    request_get as rg, database as db, memcache as mc
from config import PATH_TO_DATABASE, ACCOUNTS_ACTIVATION_VIA_MAIL, GD_SERVER_NAME, DOMAIN


whitelist_emails = ["gmail.com", "ya.ru", "yandex.by", "yandex.com",
                    "yandex.kz", "yandex.ru", "mail.ru", "internet.ru",
                    "bk.ru", "inbox.ru", "list.ru"]
whitelist = True


@account.route(f"{PATH_TO_DATABASE}/accounts/registerGJAccount.php", methods=("POST", "GET"))
def register_account():
    if not check_secret.main(
        rg.main("secret"), 0
    ):
        return "-1"

    username = regex.char_clean(rg.main("userName"))
    password = rg.main("password")
    email = rg.main("email")

    if len(username) > 15 or len(password) > 20 or \
       len(email) > 32:
        return "-1"

    if whitelist:
        if email.split("@")[1].lower() not in whitelist_emails:
            return "-1"

    if db.account.count_documents(
        {"$or": [
            {"username": {"$regex": f"^{username}$", '$options': 'i'}},
            {"email": {"$regex": f"^{email}$", '$options': 'i'}}
        ]}
    ) == 1:
        return "-1"

    account_id = last_id.main(db.account)

    if ACCOUNTS_ACTIVATION_VIA_MAIL:
        code = str(uuid.uuid4())

        message_data = {
            "title": f"Activate your account | {GD_SERVER_NAME}",
            "recipient": email,
            "body": f"Your username: {username}\nAccount activation link: {DOMAIN}/activate_account?code={code}"
        }

        sending_message = Thread(target=mail_sender.main, args=(message_data,))
        sending_message.start()

        mc.client.set(f"CT:{code}:confirm", account_id, 3600)

    sample_account = {
        "_id": account_id,
        "username": username,
        "password": passwd.password_hashing(password),
        "email": email,
        "discord_id": 0,
        "date": int(time()),
        "is_banned": 0,
        "is_valid": 0
    }

    db.account.insert_one(sample_account)

    return "1"
