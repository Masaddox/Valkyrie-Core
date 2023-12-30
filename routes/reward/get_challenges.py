from . import reward
from flask import abort
from random import randint
from datetime import datetime
from datetime import timedelta
from config import PATH_TO_DATABASE

from utils.xor import xor
from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.level_hashing import return_hash3
from utils.base64_dec_and_enc import base64_decode, base64_encode


QUESTS = [
    {"quest_type": 1, "amount": 200, "reward": (5, 25), "name": "Collect Orbs"},  # orbs
    {"quest_type": 2, "amount": 4, "reward": (5, 25), "name": "Find Coins"},      # coins
    {"quest_type": 3, "amount": 15, "reward": (5, 25), "name": "Star Master"}     # stars
]


@reward.route(f"{PATH_TO_DATABASE}/getGJChallenges.php", methods=("POST", "GET"))
def get_challenges():
    if not check_secret(
        request_get("secret"), 1
    ):
        abort(500)

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
        abort(500)

    udid = request_get("udid")
    chk = request_get("chk")

    chk = xor(base64_decode(chk[5:]), "19847")

    now = datetime.now()
    tomorrow = now + timedelta(days=1)
    tomorrow_midnight = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()

    now = now.timestamp()
    timeleft = int(tomorrow_midnight - now)

    difference = now - 977000400
    quest_id = round(difference / 86400)
    quest_id = quest_id * 3

    quests = [
        f"{quest_id + 1},{QUESTS[0]["quest_type"]},{QUESTS[0]["amount"]},{randint(*QUESTS[0]["reward"])},{QUESTS[0]["name"]}",
        f"{quest_id + 2},{QUESTS[1]["quest_type"]},{QUESTS[1]["amount"]},{randint(*QUESTS[1]["reward"])},{QUESTS[1]["name"]}",
        f"{quest_id + 3},{QUESTS[2]["quest_type"]},{QUESTS[2]["amount"]},{randint(*QUESTS[2]["reward"])},{QUESTS[2]["name"]}",
    ]

    response = ""

    response += "vcore:"
    response += f"{account_id}:"
    response += f"{chk}:"
    response += f"{udid}:"
    response += f"{account_id}:"
    response += f"{timeleft}:"
    response += f"{quests[0]}:"
    response += f"{quests[1]}:"
    response += f"{quests[2]}"

    response = base64_encode(xor(response, "19847"))
    response_hash = return_hash3(response)

    return f"vcore{response}|{response_hash}"
