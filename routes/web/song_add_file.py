import os
import shutil
from . import web
from time import time
from uuid import uuid4
from os.path import join
from flask import render_template, request
from config import (
    HCAPTCHA_SITE_KEY, PATH_TO_ROOT, PATH_TO_SONG,
    GD_SERVER_NAME, DISCORD_CONFIRMATION
)

from utils import database as db

from utils.last_id import last_id
from utils.hcaptcha import hcaptcha
from utils.passwd import check_password
from utils.request_get import request_get
from utils.request_limiter import request_limiter
from utils.regex import char_clean, clear_prohibited_chars


max_size_song = [6, 20]  # MB
time_out = [3600, 600]  # Second


@web.route("/song_add", methods=("POST", "GET"))
@web.route("/song_add/file", methods=("POST", "GET"))
def song_add_file():
    message = ""

    try:
        login = char_clean(request_get("login"))
        password = request_get("password")

        song_file = request.files["song_file"]

        if request.method != "POST":
            raise

        if len(login) > 15 or len(password) > 20:
            message = "Incorrect login or password!"
            raise

        if not hcaptcha.verify():
            message = "Captcha failed!"
            raise

        if song_file.filename == "":
            message = "You didn't upload the song!"
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
            account_id, password, is_gjp=False, fast_mode=False
        ):
            message = "Incorrect login or password!"
            raise

        vip_status = db.account_stat.find_one({"_id": account_id})["vip_status"]

        if not request_limiter(
            db.song, {"account_id": account_id, "is_local_storage": 1},
            limit_time=time_out[vip_status]
        ):
            timeout_str = "1 hour" if vip_status == 0 else "10 minutes"
            message = f"You have recently uploaded a song to the server, please wait {timeout_str}!"
            raise

        if DISCORD_CONFIRMATION:
            if db.account.count_documents({
                "_id": account_id, "discord_id": 0
            }) == 1:
                message = "You have not verified your account (read more on discord server)"
                raise

        song_filename = song_file.filename

        if len(song_filename) > 88:
            message = "Song name is more than 84 characters!"
            raise

        if song_filename[-4:] != ".mp3":
            message = "File is not in mp3 format!"
            raise

        temp_song_name = str(uuid4())
        temp_song_path = join(PATH_TO_ROOT, "data", "temp", temp_song_name + ".mp3")

        song_file.save(temp_song_path)
        song_info = os.stat(temp_song_path)

        if song_info.st_size / (1024 * 1024) > max_size_song[vip_status]:
            os.remove(temp_song_path)
            message = f"File weighs more than {max_size_song[vip_status]} megabytes!"
            raise

        song_id = last_id(db.song)

        db.song.insert_one({
            "_id": song_id,
            "name": clear_prohibited_chars(song_filename[:-4]),
            "artist_name": f"{GD_SERVER_NAME} - LocalStorage",
            "account_id": account_id,
            "link": PATH_TO_SONG + f"/{song_id}.mp3",
            "size": song_info.st_size / (1024 * 1024),
            "is_local_storage": 1,
            "upload_time": int(time())
        })

        shutil.move(temp_song_path, join(PATH_TO_ROOT, "data", "song", f"{song_id}.mp3"))

        return f"Song added successfully! Song ID = {song_id}"

    except:
        return render_template('song_add_file.html', SITE_KEY=HCAPTCHA_SITE_KEY, message=message)
