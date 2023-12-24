from . import level
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret


@level.route(f"{PATH_TO_DATABASE}/rateGJDemon21.php", methods=("POST", "GET"))
def rate_demon():
    if not check_secret(
        request_get("secret"), 3
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    level_id = request_get("levelID", "int")
    demon_type = request_get("rating", "int")

    if not check_password(
        account_id, password
    ):
        return "-1"

    if db.role_assign.count_documents({
        "_id": account_id
    }) == 0:
        return "-1"

    if db.level.count_documents({
        "_id": level_id, "is_deleted": 0
    }) == 0:
        return "-1"

    if demon_type < 0 or demon_type > 5:
        return "-1"

    db.level.update_one({"_id": level_id}, {"$set": {
        "demon_type": demon_type
    }})

    return str(level_id)
