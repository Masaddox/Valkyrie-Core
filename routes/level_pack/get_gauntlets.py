from . import level_pack
from config import PATH_TO_DATABASE

from utils import database as db

from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.level_hashing import return_hash
from utils.response_processing import resp_proc


@level_pack.route(f"{PATH_TO_DATABASE}/getGJGauntlets21.php", methods=("POST", "GET"))
def get_gauntlets():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "1"

    gauntlets = tuple(db.gauntlet.find())

    response = ""
    hash_string = ""

    for gn in gauntlets:
        single_response = {
            1: gn["_id"], 3: gn["levels"]
        }

        hash_string += f"{gn['_id']}{gn['levels']}"
        response += resp_proc(single_response) + "|"

    response = response[:-1] + f"#{return_hash(hash_string)}"

    return response
