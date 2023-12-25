from utils.request_get import request_get


AVAILABLE_VERSIONS = [21, 22]


def check_version():
    version = request_get("gameVersion", "int")

    for ver in AVAILABLE_VERSIONS:
        if ver == version:
            return version
    else:
        return 0
