from . import comment
from time import time
from config import PATH_TO_DATABASE

from utils import database as db

from utils.last_id import last_id
from utils.commands import mod_commands
from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.request_limiter import request_limiter
from utils.base64_dec_and_enc import base64_decode, base64_encode


@comment.route(f"{PATH_TO_DATABASE}/uploadGJComment21.php", methods=("POST", "GET"))
def upload_comment():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    level_comment = request_get("comment")
    level_id = request_get("levelID", "int")
    percent = request_get("percent", "int")

    level_comment_decode = base64_decode(level_comment)

    if not check_password(
        account_id, password
    ):
        return "-1"

    if not request_limiter(
        db.level_comment, {"account_id": account_id}, limit_time=15
    ):
        return "-1"

    if len(level_comment_decode) > 140 or len(level_comment_decode) == 0:
        return "-1"

    if percent > 100 or percent < 0:
        return "-1"

    if db.level.count_documents({
        "_id": level_id, "is_deleted": 0
    }) == 0:
        return "-1"

    if level_comment_decode[0] == "!":  # Команда
        mod_commands(account_id, level_id, level_comment_decode)
        return "-1"

    sample_comment = {
        "_id": last_id(db.level_comment),
        "account_id": account_id,
        "level_id": level_id,
        "comment": base64_encode(level_comment),
        "percent": percent,
        "likes": 0,
        "upload_time": int(time())
    }

    db.level_comment.insert_one(sample_comment)
    return "1"
