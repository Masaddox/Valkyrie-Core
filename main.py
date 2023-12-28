from routes import *
from flask import Flask
from utils import hcaptcha
from config import IP, PORT, DEBUG, MAX_CONTENT_LENGTH


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

hcaptcha.init_hc(app)

for route in (
    account, comment, level, level_pack, message,
    misc, relationship, reward, score, user, web
):
    app.register_blueprint(route)

if __name__ == "__main__":
    app.run(
        host=IP,
        port=PORT,
        debug=DEBUG
    )
