from time import time


def request_limiter(coll, query, main_id="_id", date="upload_time", limit_time=60):
    try:
        last_loaded = tuple(coll.find(query).sort(main_id, -1).limit(1))

        if last_loaded is not None and \
           int(time()) - last_loaded[0][date] < limit_time:
            return False
        return True
    except IndexError:
        return True
