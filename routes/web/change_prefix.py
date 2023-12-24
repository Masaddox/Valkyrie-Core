from . import web
from config import HCAPTCHA_SITE_KEY
from flask import render_template, request

from utils import database as db

from utils.regex import char_clean
from utils.hcaptcha import hcaptcha
from utils.passwd import check_password
from utils.request_get import request_get


@web.route("/change_prefix", methods=("POST", "GET"))
def change_prefix():
    message = ""

    try:
        login = char_clean(request_get("login"))
        password = request_get("password")

        prefix = request_get("prefix")

        if request.method != "POST":
            raise

        if len(login) > 15 or len(password) > 20:
            message = "Incorrect login or password!"
            raise

        if len(prefix) > 20:
            message = "Prefix exceeds 20 characters!"
            raise

        if not hcaptcha.verify():
            message = "Captcha failed!"
            raise

        account_id = tuple(db.account.find(
            {"username": {"$regex": f"^{login}$", '$options': 'i'}}
        ))

        if not bool(account_id):
            message = "Incorrect login or password!"
            raise
        else:
            account_id = account_id[0]["_id"]

        if not check_password(
            account_id, password, is_gjp=False
        ):
            message = "Incorrect login or password!"
            raise

        vip_status = db.account_stat.find_one({"_id": account_id})["vip_status"]

        if not bool(vip_status):
            message = "Vip status is required to change prefix (more details in discord server)!"
            raise

        db.account_stat.update_one({"_id": account_id}, {"$set": {
            "prefix": prefix
        }})

        return "Prefix has been successfully changed!"

    except:
        return render_template('change_prefix.html', SITE_KEY=HCAPTCHA_SITE_KEY, message=message)
