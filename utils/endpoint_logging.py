import json
import uuid
from os.path import join
from flask import request
from datetime import datetime
from utils.request_get import get_ip
from config import PATH_TO_ROOT, LOG_STATUS


black_list = ["password", "gjp", "levelString"]


def logging(status, work_result="NONE"):
    if LOG_STATUS == 0:
        return None
    elif LOG_STATUS == 1 and status != "ERROR":
        return None
    elif LOG_STATUS == 2 and status not in ("ERROR", "WARNING"):
        return None

    current_time = datetime.now()
    date = f"{current_time.hour};{current_time.minute};{current_time.second} " \
           f"{current_time.day}.{current_time.month}.{current_time.year}"

    log_name = f"{status} [{date}] {str(uuid.uuid4())}"

    data = {
        "values": request.values.to_dict(),
        "form": request.form.to_dict(),
        "args": request.args.to_dict()
    }

    for i in data:
        for j in black_list:
            if data[i].get(j) is not None:
                data[i][j] = "This value is hidden."
            else:
                continue

    log = {
        "status": status,
        "endpoint_path": request.path,
        "ip": get_ip(),
        "date": date,
        "data": data,
        "result": work_result
    }

    with open(
        join(PATH_TO_ROOT, "data", "log", f"{log_name}.log"),
        "w", encoding="utf-8"
    ) as file:
        json.dump(log, file)
