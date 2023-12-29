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
    demon_type = request_get("rating", "int")

    if db.level.count_documents({
        "_id": level_id, "is_deleted": 0
    }) == 0:
        return "-1"

    try:
        role_id = db.role_assign.find_one({"_id": account_id})["role_id"]
    except IndexError:
        return "1"

    access = db.role.find_one({"_id": role_id})["command_access"]["rate_demon_button"]

    match access:
        case 1:  # Отправка на оценку
            return "1"  # Заглушка
        case 2:
            if demon_type > 5 or demon_type < 1:
                demon_type = 3

            db.level.update_one({"_id": level_id}, {"$set": {
                "demon_type": demon_type
            }})

    return str(level_id)
