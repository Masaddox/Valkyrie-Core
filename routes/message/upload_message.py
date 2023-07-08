from . import message
from time import time
from config import PATH_TO_DATABASE
from utils import check_secret, passwd, last_id, request_get as rg, \
    database as db, encoding as enc, request_limiter as rl


@message.route(f"{PATH_TO_DATABASE}/uploadGJMessage20.php", methods=("POST", "GET"))
def upload_message():
    if not check_secret.main(
        rg.main("secret"), 1
    ):
        return "-1"

    account_id = rg.main("accountID", "int")
    password = rg.main("gjp")

    if not passwd.check_password(
        account_id, password
    ):
        return "-1"

    recipient_id = rg.main("toAccountID", "int")

    if account_id == recipient_id:
        return "-1"

    if not rl.main(
        db.message, {"account_id": account_id}, limit_time=30
    ):
        return "-1"

    subject = rg.main("subject")
    body = rg.main("body")

    subject_decode = enc.base64_decode(subject)
    body_decode = enc.xor(enc.base64_decode(body), "14251")

    if len(subject_decode) > 35 or len(subject_decode) == 0:
        return "-1"
    if len(body_decode) > 200 or len(body_decode) == 0:
        return "-1"

    try:
        message_state = db.account_stat.find_one({"_id": recipient_id})["message_state"]
    except:
        return "-1"

    if db.block_list.count_documents({"$or": [
        {"_id": recipient_id, "block_list": {"$in": (account_id,)}},
        {"_id": account_id, "block_list": {"$in": (recipient_id,)}}
    ]}) == 1:
        return "-1"

    if message_state == 1:
        if db.friend_list.count_documents({
            "_id": account_id, "friend_list": {"$in": (recipient_id,)}
        }) == 0:
            return "-1"
    elif message_state == 2:
        return "-1"

    db.message.insert_one({
        "_id": last_id.main(db.message),
        "account_id": account_id,
        "recipient_id": recipient_id,
        "subject": subject,
        "body": body,
        "is_read": 0,
        "upload_time": int(time())
    })

    db.account_stat.update_one({"_id": recipient_id}, {"$inc": {
        "missed_messages": 1
    }})

    return "1"
