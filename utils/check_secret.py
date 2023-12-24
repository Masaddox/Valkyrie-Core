all_secrets = [
    "Wmfv3899gc9", "Wmfd2893gb7", "Wmfv2898gc9", "Wmfp3879gc3"
]


def check_secret(secret, type_secret):
    if secret == all_secrets[type_secret]:
        return True
    else:
        return False
