from dotenv import load_dotenv
from os import getcwd, listdir, getenv


env_is_not_exist = True

for file in listdir(r"D:\Code\Valkyrie-Core"):
    if file == ".env":
        load_dotenv()
        env_is_not_exist = False
        break
    else:
        continue


# == Server settings ==

IP = "0.0.0.0"
PORT = "80"
DEBUG = False

MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max

GD_SERVER_NAME = "Geometry Dash Private Server"
DISCORD_SERVER_LINK = "https://discord.com/"

DOMAIN = "https://127.0.0.1:5000"  # https://example.com

PATH_TO_API = "/api"
PATH_TO_ROOT = getcwd()
PATH_TO_SONG = DOMAIN + "/song"
PATH_TO_DATABASE = "/database/db"

COMMAND_PREFIX = "!"

# == ==

# == Secret settings ==

ACCOUNTS_ACTIVATION_VIA_MAIL = False

MAIL_SERVER = "" if env_is_not_exist else getenv("MAIL_SERVER")  # only TLS
MAIL_USERNAME = "" if env_is_not_exist else getenv("MAIL_USERNAME")
MAIL_PASSWORD = "" if env_is_not_exist else getenv("MAIL_PASSWORD")
MAIL_PORT = 0 if env_is_not_exist else getenv("MAIL_PORT")

MONGO_URI = "" if env_is_not_exist else getenv("MONGO_URI")
MONGO_NAME = "" if env_is_not_exist else getenv("MONGO_NAME")

REDIS_HOST = "" if env_is_not_exist else getenv("REDIS_HOST")
REDIS_PORT = 0 if env_is_not_exist else getenv("REDIS_PORT")
REDIS_PASSWORD = "" if env_is_not_exist else getenv("REDIS_PASSWORD")
REDIS_PREFIX = "EUPH"

HCAPTCHA_SITE_KEY = "" if env_is_not_exist else getenv("HCAPTCHA_SITE_KEY")
HCAPTCHA_SECRET_KEY = "" if env_is_not_exist else getenv("HCAPTCHA_SECRET_KEY")

# == ==

# == Security settings ==

LOG_STATUS = 0  # 0 - выключить логирование
# 1 - логирование только ошибок
# 2 - логирование ошибок и предупреждений
# 3 - логирование всего

PROTECTION_AGAINST_DISLIKE_BOTS = False  # включить её только в крайнем случае!!!
# При True в like_item проходит проверка (только для уровней).
# Если уровень не был ранее загружен пользователем, то не изменять счётчик лайков.

DISCORD_CONFIRMATION = False  # В некоторых эндпоитнах (напр. Добавление музыки)
# Будет требоваться привязка дискорд аккаунта к гд аккаунту

# == ==
