from . import user
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.limit_check import limit_check
from utils.check_secret import check_secret


@user.route(f"{PATH_TO_DATABASE}/updateGJAccSettings20.php", methods=("POST", "GET"))
def update_account_settings():
    if not check_secret(
        request_get("secret"), 0
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    if not check_password(
        account_id, password
    ):
        return "-1"

    message_status = request_get("mS", "int")
    friend_status = request_get("frS", "int")
    comment_status = request_get("cS", "int")

    youtube_link = request_get("yt")
    twitter_link = request_get("twitter")
    twitch_link = request_get("twitch")

    if not limit_check(
        (message_status, 2), (friend_status, 1), (comment_status, 2),
        (len(youtube_link), 30), (len(twitter_link), 20), (len(twitch_link), 30)
    ):
        return "-1"

    db.account_stat.update_one({"_id": account_id}, {"$set": {
        "message_state": message_status,
        "friends_state": friend_status,
        "comment_history_state": comment_status,
        "youtube": youtube_link,
        "twitter": twitter_link,
        "twitch": twitch_link
    }})

    return "1"
