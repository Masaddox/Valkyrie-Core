from . import comment
from time import time
from flask import abort
from config import PATH_TO_DATABASE

from utils import database as db

from utils.last_id import last_id
from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.request_limiter import request_limiter
from utils.base64_dec_and_enc import base64_decode


@comment.route(f"{PATH_TO_DATABASE}/uploadGJAccComment20.php", methods=("POST", "GET"))
def upload_account_comment():
    if not check_secret(
        request_get("secret"), 1
    ):
        abort(500)

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    is_gjp2 = False

    if request_get("gjp2") != "":
        is_gjp2 = True
        password = request_get("gjp2")

    if not check_password(
            account_id, password,
            is_gjp=not is_gjp2, is_gjp2=is_gjp2
    ):
        abort(500)

    account_comment = request_get("comment")
    account_comment_decode = base64_decode(account_comment)

    if not request_limiter(
        db.account_comment, {"account_id": account_id}
    ):
        abort(500)

    if len(account_comment_decode) > 140 or len(account_comment_decode) == 0:
        abort(500)

    sample_comment = {
        "_id": last_id(db.account_comment),
        "account_id": account_id,
        "comment": account_comment,
        "likes": 0,
        "is_deleted": 0,
        "upload_time": int(time())
    }

    db.account_comment.insert_one(sample_comment)
    return "1"
