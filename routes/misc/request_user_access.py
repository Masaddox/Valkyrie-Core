from . import misc
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret


@misc.route(f"{PATH_TO_DATABASE}/requestUserAccess.php", methods=("POST", "GET"))
def request_user_access():
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
        account_id, password, fast_mode=False,
        is_gjp=not is_gjp2, is_gjp2=is_gjp2
    ):
        return "-1"

    if db.role_assign.count_documents({
        "_id": account_id
    }) == 0:
        return "-1"

    role_id = db.role_assign.find_one({"_id": account_id})["role_id"]
    role = db.role.find({"_id": role_id})

    badge = 2 if role[0]["mod_level"] > 1 else 1

    db.account_stat.update_one({"_id": account_id}, {"$set": {
        "mod_level": badge,
        "comment_color": role[0]["comment_color"]
    }})

    return str(badge)
