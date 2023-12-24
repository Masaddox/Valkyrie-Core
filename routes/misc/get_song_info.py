from . import misc
from config import PATH_TO_DATABASE

from utils import database as db

from utils.request_get import request_get
from utils.check_secret import check_secret
from utils.response_processing import resp_proc


@misc.route(f"{PATH_TO_DATABASE}/getGJSongInfo.php", methods=("POST", "GET"))
def get_song_info():
    if not check_secret(
        request_get("secret"), 1
    ):
        return "-1"

    song_id = request_get("songID", "int")

    if db.song.count_documents({
        "_id": song_id
    }) == 0:
        return "-1"

    response = ""

    song_info = db.song.find({"_id": song_id})[0]
    single_song = {
        1: song_info["_id"], 2: song_info["name"], 3: 0,
        4: song_info["artist_name"], 5: "{0:.2f}".format(song_info["size"]),
        6: "", 10: song_info["link"], 7: "", 8: 0
    }

    response += resp_proc(single_song, 3)[:-2]

    return response
