import hashlib
from icecream import ic
from config import REDIS_PREFIX
from bcrypt import hashpw, gensalt, checkpw

from utils import database as db

from utils.xor import xor
from utils.request_get import get_ip
from utils.redis_db import client as rd
from utils.base64_dec_and_enc import base64_decode


PASSWORD_TIMELINE = 3600


def decoding_gjp(gjp):
    return xor(base64_decode(gjp), "37526")


def password_hashing(password):
    return hashpw(password.encode(), gensalt()).decode('ascii')


def generate_gjp2(password, bcrypt=False):
    gjp2 = hashlib.sha1(bytes(password + 'mI29fmAnxgTs', 'utf-8')).hexdigest()
    gjp2 = password_hashing(gjp2) if bcrypt else gjp2

    return gjp2


def check_password(account_id, password, ip=None,
                   is_gjp=True, is_check_valid=True, fast_mode=True,
                   is_gjp2=False):
    if fast_mode:
        ip = get_ip() if ip is None else ip

        if rd.get(f"{REDIS_PREFIX}:{account_id}:passwd") == ip:
            ic()
            return True

    if account_id <= 0 or account_id is None:
        ic()
        return False

    if len(password) > 100:
        ic()
        return False

    if db.account.count_documents(
        {"_id": account_id, "is_banned": 1}
    ) == 1:
        ic()
        return False

    if is_check_valid:
        if db.account.count_documents({
            "_id": account_id, "is_valid": 0
        }) == 1:
            ic()
            return False

    if is_gjp:
        ic()
        is_gjp2 = False
        password = decoding_gjp(password)

    try:
        if checkpw(
            password.encode(),
            db.account.find_one(
                {"_id": account_id}
            )["gjp2" if is_gjp2 else "password"].encode()
        ):
            ic()
            if is_check_valid and fast_mode:
                rd.set(f"{REDIS_PREFIX}:{account_id}:passwd", ip, PASSWORD_TIMELINE)
            return True
        else:
            ic()
            return False
    except TypeError:
        ic()
        return False
