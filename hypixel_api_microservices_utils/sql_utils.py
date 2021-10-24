import sqlite3
from json import loads, dumps
from time import time
from os import getcwd
try:
    from hypixel_api_microservices_utils.hypixel_data_objs import BasicItem, Reforge, Enchant, EnchantType, Rune, RuneType, Tier, Statistics
    from hypixel_api_microservices_utils.logs_obj import init_a_new_logger
except:
    from hypixel_data_objs import BasicItem, Reforge, Enchant, EnchantType, Rune, RuneType, Tier, Statistics
    from logs_obj import init_a_new_logger

logger = init_a_new_logger("SQL Utils HAM")

if getcwd() == "C:\\Users\\lucie\\Documents\\Projets code\\auction-bot-rewrite":
    db_directory = "C:/Users/lucie/Documents/Projets code/auction-bot-rewrite/testDB.db"
else:
    db_directory = "/home/ubuntu/Advanced_Auction_DB.db"

def save_sold_history():
    def modify_into_db(cursor, key, value):
        cursor.execute(f"UPDATE sold_history SET value='{value}', update_time='{time()}' WHERE key='{key}'")

    logger.debug("saving sold history")
    db = sqlite3.connect(db_directory)

    cursor = db.cursor()
    
    basic_items_dict = {} #id str: {Tier.id str: {dungeon_level int: estimated_price_sold_hist: list}}
    for basic_item_id, by_id in BasicItem.basicitem_dict.items():
        if basic_item_id not in basic_items_dict:
            basic_items_dict[basic_item_id] = {}
        for tier, by_tier in by_id.items():
            if tier.tier_id not in basic_items_dict[basic_item_id]:
                basic_items_dict[basic_item_id][tier.tier_id] = {}
            for dungeon_level, basic_item in by_tier.items():
                basic_items_dict[basic_item_id][tier.tier_id][dungeon_level] = basic_item.estimated_price_sold_hist.raw_hist
    #print(basic_items_dict)
    
    """cursor.execute("DELETE FROM sold_history WHERE key='basic_items';")
    cursor.execute(f"INSERT INTO sold_history VALUES ('basic_items', '{dumps(basic_items_dict)}', {time()});")"""
    modify_into_db(cursor, "basic_items", dumps(basic_items_dict))
    del(basic_items_dict)
    
    reforges_dict = {}
    for reforge in tuple(Reforge.reforge_dict.values()):
        reforges_dict[reforge.reforge_id] = reforge.estimated_price_sold_hist.raw_hist

    """cursor.execute("DELETE FROM sold_history WHERE key='reforges';")
    cursor.execute(f"INSERT INTO sold_history VALUES ('reforges', '{dumps(reforges_dict)}', {time()});")"""
    modify_into_db(cursor, "reforges", dumps(reforges_dict))
    del(reforges_dict)

    enchants = {}
    for enchant_type_obj_by_enchant_type in tuple(EnchantType.enchant_type_dict.values()):
        for enchant_type_obj in tuple(enchant_type_obj_by_enchant_type.values()):
            for enchant in tuple(enchant_type_obj.enchant_by_levels_dict.values()):
                if enchant_type_obj.enchant_type_id not in enchants:
                    enchants[enchant_type_obj.enchant_type_id] = {}
                if enchant_type_obj.enchant_type not in enchants[enchant_type_obj.enchant_type_id]:
                    enchants[enchant_type_obj.enchant_type_id][enchant_type_obj.enchant_type] = {}
                enchants[enchant_type_obj.enchant_type_id][enchant_type_obj.enchant_type][enchant.level] = enchant.estimated_price_sold_hist.raw_hist
    
    """cursor.execute("DELETE FROM sold_history WHERE key='enchants';")
    cursor.execute(f"INSERT INTO sold_history VALUES ('enchants', '{dumps(enchants)}', {time()});")"""
    modify_into_db(cursor, "enchants", dumps(enchants))
    del(enchants)

    runes = {}
    for rune_type in tuple(RuneType.rune_type_dict.values()):
        for rune in tuple(rune_type.rune_by_levels_dict.values()):
            if rune_type.rune_type_id not in runes:
                runes[rune_type.rune_type_id] = {}
            runes[rune_type.rune_type_id][rune.level] = rune.estimated_price_sold_hist.raw_hist
    
    """cursor.execute("DELETE FROM sold_history WHERE key='runes';")
    cursor.execute(f"INSERT INTO sold_history VALUES ('runes', '{dumps(runes)}', {time()});")"""
    modify_into_db(cursor, "runes", dumps(runes))
    del(runes)

    #TODO specialized and unspecialized data
    
    db.commit()

    cursor.close()

def save_stats():
    logger.debug("saving stats")
    db = sqlite3.connect(db_directory)

    cursor = db.cursor()

    for key, value in tuple(Statistics.dict.items()):
        cursor.execute(f"UPDATE ham_stats SET value='{dumps(value)}', update_time='{time()}' WHERE key='{dumps(key)}';")

    db.commit()
    logger.debug("saved stats")

def load_sold_history():
    logger.debug("loading sold history")
    db = sqlite3.connect(db_directory)

    cursor = db.cursor()

    def get_something(key_to_get, loader):
        cursor.execute(f"SELECT value FROM sold_history WHERE key='{key_to_get}'")
        value_got = cursor.fetchone()
        if value_got is None:
            logger.error(f"key {key_to_get} not found on db")
        else:
            loader(value_got[0])

    get_something("basic_items", BasicItem.loader)
    logger.debug(f"loaded {len(BasicItem.basicitem_dict)} basic items")
    get_something("reforges", Reforge.loader)
    logger.debug(f"loaded {len(Reforge.reforge_dict)} reforges")
    get_something("enchants", EnchantType.loader)
    logger.debug(f"loaded {len(EnchantType.enchant_type_dict)} enchant types")
    get_something("runes", RuneType.loader)
    logger.debug(f"loaded {len(RuneType.rune_type_dict)} rune types")

def load_stats():
    logger.debug("loading stats")
    db = sqlite3.connect(db_directory)

    cursor = db.cursor()

    cursor.execute("SELECT key, value FROM ham_stats")
    data = cursor.fetchall()
    for key, value in data:
        Statistics.dict[loads(key)] = loads(value)
    
    logger.debug(f"loaded {len(data)} stats")


"""load_sold_history()
print(BasicItem.basicitem_dict)
print(Reforge.get_reforge("fierce").estimated_price_sold_hist.raw_hist)
print(BasicItem.get_basicitem("LUXURIOUS_SPOOL", Tier.get_tier("RARE"), 0).estimated_price_sold_hist.get_median(None))
print(EnchantType.get_enchant_type("protection").get_enchant(5).estimated_price_sold_hist.raw_hist)
print(RuneType.get_rune_type("COUTURE").rune_by_levels_dict)"""