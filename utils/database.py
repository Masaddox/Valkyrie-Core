from config import *
from pymongo import MongoClient


db = MongoClient(MONGO_URI)
current_db = db[MONGO_NAME]

action_download = current_db["action_download"]
account_comment = current_db["account_comment"]
level_comment = current_db["level_comment"]
account_stat = current_db["account_stat"]
suggest = current_db["suggested_level"]
daily_level = current_db["daily_level"]
role_assign = current_db["role_assign"]
action_like = current_db["action_like"]
friend_list = current_db["friend_list"]
master_key = current_db["master_key"]
friend_req = current_db["friend_req"]
block_list = current_db["block_list"]
level_list = current_db["level_list"]
banned_ip = current_db["banned_ip"]
gauntlet = current_db["gauntlet"]
map_pack = current_db["map_pack"]
account = current_db["account"]
message = current_db["message"]
level = current_db["level"]
song = current_db["song"]
role = current_db["role"]
log = current_db["log"]
