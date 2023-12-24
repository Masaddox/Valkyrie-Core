from . import relationship
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret


@relationship.route(f"{PATH_TO_DATABASE}/unblockGJUser20.php", methods=("POST", "GET"))
def unblock_user():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    if not check_password(
        account_id, password
    ):
        return "1"

    target_id = request_get("targetAccountID", "int")

    if account_id == target_id:
        return "1"

    if db.block_list.count_documents({
        "_id": account_id, "block_list": {"$in": (target_id,)}
    }) == 1:
        db.block_list.update_one({"_id": account_id}, {"$pull": {"block_list": target_id}})

    return "1"
