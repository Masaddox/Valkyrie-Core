def last_id(coll, string="_id"):
    last_id_int = coll.find().sort('_id', -1).limit(1)
    try:
        return last_id_int[0][string] + 1
    except IndexError:
        return 1
