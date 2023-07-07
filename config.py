from os import getcwd


# Основные настройки

IP = "0.0.0.0"
PORT = "80"
DEBUG = False

MAX_CONTENT_LENGTH = 50 * 1024 * 1024

GD_SERVER_NAME = "Geometry Dash Private Server"
DISCORD_SERVER_LINK = "https://discord.com/"

# Пути

DOMAIN = ""  # Example "https://example.com"

PATH_TO_ROOT = getcwd()
PATH_TO_SONG = DOMAIN + "/song"
PATH_TO_DATABASE = "/database/db"

# Почта

ACCOUNTS_ACTIVATION_VIA_MAIL = False

MAIL_SERVER = "mail.example.ru"
MAIL_USERNAME = "admin@example.com"
MAIL_PASSWORD = "password"
MAIL_USE_TLS = True
MAIL_PORT = 465

# База данных (mongodb)

MONGO_URI = "mongodb://localhost:27017/"
MONGO_NAME = "vcore"

# База данных (memcache)

MEMCACHE_LIFETIME = 3600

# Капча

HCAPTCHA_SITE_KEY = ""
HCAPTCHA_SECRET_KEY = ""

# Остальное

LOG_STATUS = 0  # 0 - выключить логирование
# 1 - логирование только ошибок
# 2 - логирование ошибок и предупреждений
# 3 - логирование всего

PROTECTION_AGAINST_DISLIKE_BOTS = False  # включить её только в крайнем случае!!!
# При True в like_item проходит проверка (только для уровней).
# Если уровень не был ранее загружен пользователем, то не изменять счётчик лайков.
