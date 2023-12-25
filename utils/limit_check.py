def limit_check(*args):
    for arg in args:
        if 0 <= arg[0] <= arg[1]:
            continue
        else:
            return False
    else:
        return True


def new_limit_check(*args):
    for arg in args:
        if arg[0] <= arg[1] <= arg[2]:
            continue
        else:
            return False
    else:
        return True
