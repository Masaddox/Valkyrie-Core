import re
from flask import request


def request_get(arg, arg_type="str"):
    received_data = request.values.get(arg)

    if received_data is None:
        if arg_type == "str" or arg_type == "link":
            return ""
        elif arg_type == "int":
            return 0
        else:
            return ""

    if arg_type == "str" or arg_type == "link":
        forbidden_symbols = r"[~:|#]" if arg_type == "str" else r"[~|#]"
        return re.sub(forbidden_symbols, "", received_data)
    elif arg_type == "int":
        try:
            return int(received_data)
        except ValueError:
            return 0
    else:
        return ""


def get_ip():
    return request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr).split(",")[0]
