from . import comment
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret


@comment.route(f"{PATH_TO_DATABASE}/deleteGJAccComment20.php", methods=("POST", "GET"))
def delete_account_comments():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    comment_id = request_get("commentID", "int")

    if not check_password(
        account_id, password
    ):
        return "-1"

    if db.account_comment.count_documents({
        "_id": comment_id, "account_id": account_id
    }) == 0:
        return "-1"

    db.account_comment.delete_one({"_id": comment_id})

    return "1"
