from . import user
from config import PATH_TO_DATABASE

from utils import database as db

from utils.regex import char_clean
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.response_processing import resp_proc


@user.route(f"{PATH_TO_DATABASE}/getGJUsers20.php", methods=("POST", "GET"))
def get_users():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    search_str = char_clean(request_get("str"))
    page = request_get("page", "int")

    offset = page * 10

    query = {
        "username": {"$regex": f"^{search_str}$", '$options': 'i'}
    }

    if db.account_stat.count_documents(query) == 0:
        return "-1"

    users = tuple(db.account_stat.find(query).skip(offset).limit(10))

    response = ""

    for i in users:
        single_user = {
            1: i["username"], 2: i["_id"], 13: i["secret_coins"], 17: i["user_coins"], 6: "", 9: i["icon_id"],
            10: i["first_color"], 11: i["second_color"], 14: i["icon_type"], 15: 0, 16: i["_id"], 3: i["stars"],
            8: i["creator_points"], 4: ["demons"]
        }
        response += resp_proc(single_user) + "|"

    response = response[:-1] + f"#{db.account_stat.count_documents(query)}:{offset}:10"
    return response
