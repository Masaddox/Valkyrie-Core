from . import comment
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret


@comment.route(f"{PATH_TO_DATABASE}/deleteGJComment20.php", methods=("POST", "GET"))
def delete_comment():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

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
        return "-1"

    level_id = request_get("levelID", "int")
    comment_id = request_get("commentID", "int")

    if db.level_comment.count_documents({
        "_id": comment_id, "level_id": level_id
    }) == 1:

        if db.level.count_documents({
            "_id": level_id, "account_id": account_id
        }) == 1:  # Если это твой уровень, то удалить комментарий можно
            pass

        elif db.level_comment.count_documents({
            "_id": comment_id, "account_id": account_id,
            "level_id": level_id
        }) == 0:  # Иначе, если это не твой комментарий, то пошёл куда подальше
            return "-1"

    else:
        return "-1"

    db.level_comment.delete_one({"_id": comment_id})
    return "1"
