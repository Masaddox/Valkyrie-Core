from . import user
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.limit_check import limit_check
from utils.check_secret import check_secret


"""
RUS: Обязательно меняйте лимиты при росте приватного сервера!
ENG: Be sure to change the limits as your private server grows!
"""

limits = {
    "stars": 5000,
    "demons": 500,
    "diamonds": 999999999,
    "user_coins": 1000,
    "secret_coins": 100
}


@user.route(f"{PATH_TO_DATABASE}/updateGJUserScore22.php", methods=("POST", "GET"))
def update_user_score():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    account_id = request_get("accountID", "int")
    password = request_get("gjp")

    if not check_password(
        account_id, password
    ):
        return "-1"

    start = request_get("stars", "int")
    demons = request_get("demons", "int")
    diamonds = request_get("diamonds", "int")
    user_coins = request_get("userCoins", "int")
    secret_coins = request_get("coins", "int")

    icon_type = request_get("iconType", "int")  # 6
    icon_id = request_get("icon", "int")  # 142
    icon_cube = request_get("accIcon", "int")  # 142
    icon_ship = request_get("accShip", "int")  # 51
    icon_ball = request_get("accBall", "int")  # 43
    icon_ufo = request_get("accBird", "int")  # 35
    icon_wave = request_get("accDart", "int")  # 35
    icon_robot = request_get("accRobot", "int")  # 26
    icon_spider = request_get("accSpider", "int")  # 17
    icon_glow = request_get("accGlow", "int")  # 1
    first_color = request_get("color1", "int")  # 41
    second_color = request_get("color2", "int")  # 41

    if not limit_check(
        (start, limits["stars"]), (demons, limits["demons"]), (diamonds, limits["diamonds"]),
        (user_coins, limits["user_coins"]), (secret_coins, limits["secret_coins"]), (icon_type, 6),
        (icon_id, 142), (icon_cube, 142), (icon_ship, 51), (icon_ball, 43), (icon_ufo, 35), (icon_wave, 35),
        (icon_robot, 26), (icon_spider, 17), (icon_glow, 1), (first_color, 41), (second_color, 41)
    ):
        return "-1"

    db.account_stat.update_one({"_id": account_id}, {"$set": {
        "stars": start,
        "demons": demons,
        "diamonds": diamonds,
        "user_coins": user_coins,
        "secret_coins": secret_coins,
        "icon_id": icon_id,
        "icon_type": icon_type,
        "icon_cube": icon_cube,
        "icon_ship": icon_ship,
        "icon_ball": icon_ball,
        "icon_ufo": icon_ufo,
        "icon_wave": icon_wave,
        "icon_robot": icon_robot,
        "icon_spider": icon_spider,
        "icon_glow": icon_glow,
        "first_color": first_color,
        "second_color": second_color
    }})

    return str(account_id)
