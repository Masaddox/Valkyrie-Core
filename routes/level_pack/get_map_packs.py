from . import level_pack
from pymongo import ASCENDING
from config import PATH_TO_DATABASE

from utils import database as db

from utils.request_get import request_get
from utils.level_hashing import return_hash
from utils.check_secret import check_secret
from utils.response_processing import resp_proc


@level_pack.route(f"{PATH_TO_DATABASE}/getGJMapPacks21.php", methods=("POST", "GET"))
def get_map_packs():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "1"

    page = request_get("page", "int")
    offset = page * 10

    response = ""
    hash_string = ""

    map_packs = tuple(db.map_pack.find().skip(offset).limit(10).sort([("_id", ASCENDING)]))

    for mp in map_packs:
        single_response = {
            1: mp["_id"], 2: mp["name"], 3: mp["levels"], 4: mp["stars"], 5: mp["coins"],
            6: mp["difficulty"], 7: mp["text_color"], 8: mp["bar_color"]
        }

        response += resp_proc(single_response) + "|"
        hash_string += f"{str(mp['_id'])[0]}{str(mp['_id'])[-1]}{mp['stars']}{mp['coins']}"

    response = response[:-1] + f"#{db.map_pack.count_documents({})}:{offset}:10#{return_hash(hash_string)}"

    return response
