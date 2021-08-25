import sqlite3
from json import loads, dumps
from time import time
try:
    from hypixel_api_microservices_utils.hypixel_data_objs import BasicItem, Reforge, Enchant, EnchantType, Rune, RuneType, Tier
    from hypixel_api_microservices_utils.logs_obj import init_a_new_logger
except:
    from hypixel_data_objs import BasicItem, Reforge, Enchant, EnchantType, Rune, RuneType, Tier
    from logs_obj import init_a_new_logger

logger = init_a_new_logger("SQL Utils HAM")

def save_sold_history():
    db = sqlite3.connect("testDB.db")

    cursor = db.cursor()
    
    basic_items_dict = {} #id str: {Tier.id str: {dungeon_level int: estimated_price_sold_hist: list}}
    for basic_item in tuple(BasicItem.basicitem_dict.values()):
        if basic_item.item_id not in basic_items_dict:
            basic_items_dict[basic_item.item_id] = {}
        if basic_item.tier.tier_id not in basic_items_dict[basic_item.item_id]:
            basic_items_dict[basic_item.item_id][basic_item.tier.tier_id] = {}
        basic_items_dict[basic_item.item_id][basic_item.tier.tier_id][basic_item.dungeon_level] = basic_item.estimated_price_sold_hist.raw_hist
    print(basic_items_dict)
    
    cursor.execute("DELETE FROM sold_history WHERE key='basic_items';")
    cursor.execute(f"INSERT INTO sold_history VALUES ('basic_items', '{dumps(basic_items_dict)}', {time()});")
    del(basic_items_dict)
    
    reforges_dict = {}
    for reforge in tuple(Reforge.reforge_dict.values()):
        reforges_dict[reforge.reforge_id] = reforge.estimated_price_sold_hist.raw_hist

    cursor.execute("DELETE FROM sold_history WHERE key='reforges';")
    cursor.execute(f"INSERT INTO sold_history VALUES ('reforges', '{dumps(reforges_dict)}', {time()});")
    del(reforges_dict)

    enchants = {}
    for enchant_type in tuple(EnchantType.enchant_type_dict.values()):
        for enchant in tuple(enchant_type.enchant_by_levels_dict.values()):
            if enchant_type.enchant_type_id not in enchants:
                enchants[enchant_type.enchant_type_id] = {}
            enchants[enchant_type.enchant_type_id][enchant.level] = enchant.estimated_price_sold_hist.raw_hist
    
    cursor.execute("DELETE FROM sold_history WHERE key='enchants';")
    cursor.execute(f"INSERT INTO sold_history VALUES ('enchants', '{dumps(enchants)}', {time()});")
    del(enchants)

    runes = {}
    for rune_type in tuple(RuneType.rune_type_dict.values()):
        for rune in tuple(rune_type.rune_by_levels_dict.values()):
            if rune_type.rune_type_id not in runes:
                runes[rune_type.rune_type_id] = {}
            runes[rune_type.rune_type_id][rune.level] = rune.estimated_price_sold_hist.raw_hist
    
    cursor.execute("DELETE FROM sold_history WHERE key='runes';")
    cursor.execute(f"INSERT INTO sold_history VALUES ('runes', '{dumps(runes)}', {time()});")
    del(runes)

    #TODO specialized and unspecialized data
    
    db.commit()

    cursor.close()

def load_sold_history():
    db = sqlite3.connect("testDB.db")

    cursor = db.cursor()

    def get_something(key_to_get, loader):
        cursor.execute(f"SELECT value FROM sold_history WHERE key='{key_to_get}'")
        value_got = cursor.fetchone()
        if value_got is None:
            logger.error(f"key {key_to_get} not found on db")
        else:
            loader(value_got[0])

    get_something("basic_items", BasicItem.loader)
    get_something("reforges", Reforge.loader)
    get_something("enchants", EnchantType.loader)
    get_something("runes", RuneType.loader)

"""load_sold_history()
print(BasicItem.basicitem_dict)
print(Reforge.get_reforge("fierce").estimated_price_sold_hist.raw_hist)
print(BasicItem.get_basicitem("LUXURIOUS_SPOOL", Tier.get_tier("RARE"), 0).estimated_price_sold_hist.get_median(None))
print(EnchantType.get_enchant_type("protection").get_enchant(5).estimated_price_sold_hist.raw_hist)
print(RuneType.get_rune_type("COUTURE").rune_by_levels_dict)"""