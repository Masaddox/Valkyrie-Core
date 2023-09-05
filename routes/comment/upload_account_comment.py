from . import comment
from time import time
from flask import abort
from config import PATH_TO_DATABASE
from utils import check_secret, request_limiter, last_id, passwd, \
    request_get as rg, database as db, encoding as enc


@comment.route(f"{PATH_TO_DATABASE}/uploadGJAccComment20.php", methods=("POST", "GET"))
def upload_account_comment():
    if not check_secret.main(
        rg.main("secret"), 1
    ):
        abort(500)

    account_id = rg.main("accountID", "int")
    password = rg.main("gjp")

    account_comment = rg.main("comment")
    account_comment_decode = enc.base64_decode(account_comment)

    if not passwd.check_password(
        account_id, password
    ):
        abort(500)

    if not request_limiter.main(
        db.account_comment, {"account_id": account_id}
    ):
        abort(500)

    if len(account_comment_decode) > 140 or len(account_comment_decode) == 0:
        abort(500)

    sample_comment = {
        "_id": last_id.main(db.account_comment),
        "account_id": account_id,
        "comment": account_comment,
        "likes": 0,
        "upload_time": int(time())
    }

    db.account_comment.insert_one(sample_comment)
    return "1"
