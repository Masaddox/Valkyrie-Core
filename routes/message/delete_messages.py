from . import message
from config import PATH_TO_DATABASE

from utils import database as db

from utils.passwd import check_password
from utils.request_get import request_get
from utils.check_secret import check_secret


@message.route(f"{PATH_TO_DATABASE}/deleteGJMessages20.php", methods=("POST", "GET"))
def delete_messages():
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

    message_id = request_get("messageID", "int")
    message_ids = request_get("messages")

    if message_ids != "":
        message_ids = message_ids.split(",")
    else:
        message_ids = None

    query = {"_id": message_id} if message_ids is None else \
            {"_id": {"$in": message_ids}}
    messages = tuple(db.message.find(query))

    for msg in messages:
        if msg["account_id"] != account_id and \
           msg["recipient_id"] != account_id:
            return "1"

        if msg["is_read"] == 0:
            db.account_stat.update_one(
                {"_id": msg["account_id"] if msg["recipient_id"] == account_id else msg["recipient_id"]},
                {"$inc": {
                    "missed_messages": -1
                }}
            )

        db.message.delete_one({"_id": msg["_id"]})

    return "1"
