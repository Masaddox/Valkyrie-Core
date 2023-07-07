from . import web
from flask import request, render_template
from utils import request_get, regex, passwd, \
    hcaptcha as hc, database as db, memcache as mc
from config import HCAPTCHA_SITE_KEY, ACCOUNTS_ACTIVATION_VIA_MAIL


@web.route("/activate_account", methods=("POST", "GET"))
def activate_account():
    message = ""

    if ACCOUNTS_ACTIVATION_VIA_MAIL:
        code = request_get.main("code")

        if code is None:
            return "Code is invalid!"

        account_id = mc.client.get(f"CT:{code}:confirm")

        if account_id is None:
            return "Code is invalid!"

        account_id = int(account_id.decode())
    else:
        try:
            username = regex.char_clean(request_get.main('login'))
            account_id = db.account.find(
                {"username": {"$regex": f"^{username}$", '$options': 'i'}})["_id"]
        except:
            message = "Wrong login!"
            raise

    try:
        if request.method == "POST":
            password = request_get.main("password")

            if not hc.hcaptcha.verify():
                message = "Captcha failed!"
                raise

            if db.account.count_documents({
                "_id": account_id, "is_valid": 1
            }) == 1:
                message = "Account already verified!"
                raise

            if not passwd.check_password(
                account_id, password,
                is_gjp=False, is_check_valid=False, fast_mode=False
            ):
                message = "Wrong password!"
                raise

            sample_account_stat = {
                "_id": account_id, "username": db.account.find_one({"_id": account_id})["username"],
                "stars": 0, "demons": 0, "diamonds": 0, "user_coins": 0, "secret_coins": 0, "creator_points": 0,
                "first_color": 0, "second_color": 3, "icon_id": 1, "icon_type": 0, "icon_cube": 1, "icon_ship": 1,
                "icon_ball": 1, "icon_ufo": 1, "icon_wave": 1, "icon_robot": 1, "icon_spider": 1, "icon_glow": 0,
                "missed_messages": 0, "friend_requests": 0, "message_state": 0, "friends_state": 0,
                "comment_history_state": 0, "youtube": "", "twitter": "", "twitch": "", "global_rank": 0,
                "is_top_banned": 0, "prefix": "", "comment_color": "", "mod_level": 0, "vip_status": 0
            }

            db.account.update_one({"_id": account_id}, {"$set": {"is_valid": 1}})
            db.account_stat.insert_one(sample_account_stat)

            if ACCOUNTS_ACTIVATION_VIA_MAIL:
                mc.client.delete(f"CT:{code}:confirm")

            return "Account verified!"
        else:
            raise
    except:
        html_file = "activate_account.html" if ACCOUNTS_ACTIVATION_VIA_MAIL else "activate_account_no_email.html"
        return render_template(html_file, SITE_KEY=HCAPTCHA_SITE_KEY, message=message)
