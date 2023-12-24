from . import level
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.base64_dec_and_enc import base64_decode


@level.route(f"{PATH_TO_DATABASE}/updateGJDesc20.php", methods=("POST", "GET"))
def update_desc():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    level_id = request_get("levelID", "int")
    level_desc = request_get("levelDesc")

    if not check_password(
        account_id, password
    ):
        return "-1"

    if db.level.count_documents({
        "_id": level_id, "account_id": account_id,
        "is_deleted": 0, "update_prohibition": 0
    }) == 0:
        return "-1"

    if len(base64_decode(level_desc)) > 140:
        return "-1"

    db.level.update_one({"_id": level_id}, {"$set": {
        "desc": level_desc
    }})

    return "1"
