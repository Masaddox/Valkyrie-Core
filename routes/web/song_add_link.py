import urllib
from . import web
from time import time
from flask import render_template, request
from config import HCAPTCHA_SITE_KEY, GD_SERVER_NAME

from utils import database as db

from utils.last_id import last_id
from utils.hcaptcha import hcaptcha
from utils.passwd import check_password
from utils.request_get import request_get
from utils.request_limiter import request_limiter
from utils.regex import char_clean, clear_prohibited_chars


time_out = [600, 180]  # Second


@web.route("/song_add/link", methods=("POST", "GET"))
def song_add_link():
    message = ""

    try:
        login = char_clean(request_get("login"))
        password = request_get("password")

        if request.method != "POST":
            raise

        song_link = request_get("song_link", "link")

        if len(login) > 15 or len(password) > 20:
            message = "Incorrect login or password!"
            raise

        if not hcaptcha.verify():
            message = "Captcha failed!"
            raise

        if len(song_link) == 0:
            message = "Song link is empty!"
            raise

        if song_link.split("/")[2] != "www.dropbox.com":
            message = "Dropbox only!"
            raise

        account_id = tuple(db.account.find(
            {"username": {"$regex": f"^{login}$", '$options': 'i'}}
        ))

        if not bool(account_id):
            message = "Incorrect login or password!"
            raise
        else:
            account_id = account_id[0]["_id"]

        if not check_password(
            account_id, password, is_gjp=False
        ):
            message = "Incorrect login or password!"
            raise

        vip_status = db.account_stat.find_one({"_id": account_id})["vip_status"]

        if not request_limiter(
            db.song, {"account_id": account_id, "is_local_storage": 0},
            limit_time=time_out[vip_status]
        ):
            timeout_str = "10 minutes" if vip_status == 0 else "3 minutes"
            message = f"You have recently uploaded a song to the server, please wait {timeout_str}!"
            raise

        song_link = song_link.replace("www.dropbox.com", "dl.dropboxusercontent.com")
        song_link = song_link.replace("?dl=0", "")
        song_link = song_link.replace("?dl=1", "")
        song_link = song_link.replace(" ", "_")
        song_link = song_link.replace("%20", "_")

        if clear_prohibited_chars(song_link.split("/")[-1:][0]) != song_link.split("/")[-1:][0]:
            message = "There are invalid characters in the song name! " \
                      "(try renaming the song with letters and numbers only.)"
            raise

        try:
            req = urllib.request.Request(song_link, method='HEAD')
        except:
            message = "There are errors in the link!"
            raise

        f = urllib.request.urlopen(req)

        if int(f.status) != 200:
            message = "Song link not working!"
            raise

        if db.song.count_documents({
            "link": song_link
        }) == 1:
            return f"The song was loaded before you. Song ID = {db.song.find_one({'link': song_link})['_id']}"

        filename = f.headers["Content-Disposition"].split(";")
        filename = filename[1].partition('=\"')[2].partition('.mp3')[0]
        filename = clear_prohibited_chars(filename)

        if len(filename) > 84:
            message = "Song name is more than 84 characters!"
            raise

        song_id = last_id(db.song)

        db.song.insert_one({
            "_id": song_id,
            "name": filename,
            "artist_name": f"{GD_SERVER_NAME} - DropBox",
            "account_id": account_id,
            "link": song_link,
            "size": float(f.headers["Content-Length"]) / (1024 * 1024),
            "is_local_storage": 0,
            "upload_time": int(time())
        })

        return f"Song added successfully! Song ID = {song_id}"

    except:
        return render_template('song_add_link.html', SITE_KEY=HCAPTCHA_SITE_KEY, message=message)
