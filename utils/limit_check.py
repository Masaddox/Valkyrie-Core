def limit_check(*args):
    for arg in args:
        if 0 <= arg[0] <= arg[1]:
            continue
        else:
            return False
    else:
        return True
