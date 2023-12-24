def resp_proc(resp_dict, type_proc=1):
    response_string = ""
    sep = ""  # separator

    if type_proc == 1:
        sep = ":"
    elif type_proc == 2:
        sep = "~"
    elif type_proc == 3:
        sep = "~|~"

    for key, value in resp_dict.items():
        response_string += f"{str(key)}{sep}{str(value)}{sep}"

    return response_string[:-1]
