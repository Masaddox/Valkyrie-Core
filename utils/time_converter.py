import time


def time_conv(timestamp):
    time_now = int(time.time())
    time_interval = time_now - timestamp

    response = ""

    if time_interval <= 59:
        response = f"{time_interval} second"
        if time_interval > 1:
            response += "s"
    elif 60 <= time_interval < 3600:
        response = f"{time_interval // 60} minute"
        if time_interval > 120:
            response += "s"
    elif 3600 <= time_interval < 86400:
        response = f"{time_interval // 3600} hour"
        if time_interval > 7200:
            response += "s"
    elif 86400 <= time_interval < 604800:
        response = f"{time_interval // 86400} day"
        if time_interval > 172800:
            response += "s"
    elif 604800 <= time_interval < 2629743:
        response = f"{time_interval // 604800} week"
        if time_interval > 1209600:
            response += "s"
    elif 2629743 <= time_interval < 31556926:
        response = f"{time_interval // 2629743} month"
        if time_interval > 5259486:
            response += "s"
    elif time_interval >= 31556926:
        response = f"{time_interval // 31556926} year"
        if time_interval > 63113852:
            response += "s"

    return response
