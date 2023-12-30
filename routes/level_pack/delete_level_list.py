from . import level_pack
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret


@level_pack.route(f"{PATH_TO_DATABASE}/deleteGJLevelList.php", methods=("POST", "GET"))
def delete_level_list():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp2")

    if not check_password(
        account_id, password, is_gjp=False, is_gjp2=True
    ):
        return "-1"

    list_id = request_get("listID", "int")

    if db.level_list.count_documents({
        "_id": list_id, "account_id": account_id, "is_deleted": 0
    }) == 0:
        return "-1"

    db.level_list.update_one({"_id": list_id}, {"$set": {
        "is_deleted": 1
    }})

    return "1"
