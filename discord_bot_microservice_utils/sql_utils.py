import sqlite3
from json import loads, dumps
from time import time
from os import getcwd
try:
    from discord_bot_microservice_utils.logs_obj import init_a_new_logger
except:
    from logs_obj import init_a_new_logger

logger = init_a_new_logger("SQL Utils DBM")

if getcwd() == "C:\\Users\\lucie\\Documents\\Projets code\\auction-bot-rewrite":
    db_directory = "C:/Users/lucie/Documents/Projets code/auction-bot-rewrite/testDB.db"
else:
    db_directory = "/home/ubuntu/Advanced_Auction_DB.db"

db = sqlite3.connect(db_directory)

def update_stat(stat_name, value, table="dbm_stats"):
    logger.debug(f"modifying stat {stat_name} to {value}")
    
    cursor = db.cursor()

    cursor.execute(f"UPDATE {table} SET value='{dumps(value)}', update_time='{time()}' WHERE key='{dumps(stat_name)}';")
    cursor.close()
    db.commit()
    logger.debug("modified stat")

def get_stat(stat_name, table="dbm_stats"):
    logger.debug("getting stat")
    cursor = db.cursor()

    cursor.execute(f"SELECT value FROM {table} WHERE key='{dumps(stat_name)}';")
    value = cursor.fetchone()[0]
    cursor.close()
    return loads(value)

def command(command):
    cursor = db.cursor()

    cursor.execute(command)
    cursor.close()
    db.commit()

"""def save_stats():
    logger.debug("saving stats")
    db = sqlite3.connect("testDB.db")

    cursor = db.cursor()

    for key, value in tuple(Statistics.dict.items()):
        cursor.execute(f"UPDATE dbm_stats SET value='{value}', update_time='{time()}' WHERE key='{key}';")
    logger.debug("saved stats")


def load_stats():
    logger.debug("loading stats")
    db = sqlite3.connect("testDB.db")

    cursor = db.cursor()

    cursor.execute("SELECT key, value FROM dbm_stats")
    data = cursor.fetchall()
    for key, value in data:
        Statistics.dict[loads(key)] = loads(value)
    
    logger.debug(f"loaded {len(data)} stats")"""