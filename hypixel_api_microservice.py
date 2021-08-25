from hypixel_api_microservices_utils.hypixel_data_objs import *
from hypixel_api_microservices_utils.logs_obj import init_a_new_logger
from hypixel_api_microservices_utils.others_objs import GlobalHAM
from hypixel_api_microservices_utils.sql_utils import save_sold_history

main_py_file_logger = init_a_new_logger("Main HAM py file")

main_py_file_logger.info("--------| Hypixel Api Microservice Starting |--------")

import sys
import os
import psutil
import threading
import time
import requests
from base64 import b64decode
from io import BytesIO
from nbt.nbt import NBTFile

HYPIXEL_API_SKYBLOCK_LINK = "https://api.hypixel.net/skyblock/"
HYPIXEL_API_AUCTIONS_LINK = HYPIXEL_API_SKYBLOCK_LINK + "auctions"
HYPIXEL_API_ENDED_AUCTIONS_LINK = HYPIXEL_API_SKYBLOCK_LINK + "auctions_ended"

python_process = psutil.Process(os.getpid())

def get_ram():
    return python_process.memory_info().rss / 1024 ** 2

def get_useful_data_from_auction(auction: dict):
    dataDecoded = b64decode(auction["item_bytes"])
    nbt_data = NBTFile(fileobj=BytesIO(dataDecoded))

    auction_attributes = {"uuid": auction["uuid"], "seller_uuid": auction["auctioneer"], "start": Timestamp(auction["start"]),
        "end": Timestamp(auction["end"]), "item_count": nbt_data["i"][0]["Count"].value, "starting_bid": auction["starting_bid"]
    }

    extra_attributes = nbt_data["i"][0]["tag"]["ExtraAttributes"]
    dungeon_lvl = 0 
    if "dungeon_item_level" in extra_attributes: dungeon_lvl = extra_attributes["dungeon_item_level"].value
    
    if "enchantments" in extra_attributes: 
        enchants = []
        for enchant in extra_attributes["enchantments"]:
            enchants.append(EnchantType.get_enchant_type(enchant).get_enchant(extra_attributes["enchantments"][enchant].value))
        enchants = tuple(enchants)
    else:
        enchants = ()
    
    if "runes" in extra_attributes: 
        runes = []
        for rune in extra_attributes["runes"]:
            runes.append(RuneType.get_rune_type(rune).get_rune(extra_attributes["runes"][rune].value))
        runes = tuple(runes)
    else:
        runes = ()
    
    reforge = None
    if "modifier" in extra_attributes: reforge = Reforge.get_reforge(extra_attributes["modifier"].value)

    basicitem_attributes = {"item_id": extra_attributes["id"].value, "tier": Tier.get_tier(auction["tier"]), "dungeon_lvl": dungeon_lvl}

    for attr in extra_attributes:
        if attr in AdditionalAttributeSpecialized.ATTRIBUTES_NAME_FOR_THIS_CLASS or attr in AdditionalAttributeUnspecialized.ATTRIBUTES_NAME_FOR_THIS_CLASS:
            #logger.debug(f"Item {auction['item_name']} skipped because of an additionnal attribute")
            return None, None

    item_attributes = {"item_name": auction["item_name"], "basicitem": BasicItem.get_basicitem(**basicitem_attributes), "reforge": reforge, "enchants": enchants, "runes": runes}
    if item_attributes["basicitem"] is None:
        return None, None
    return auction_attributes, item_attributes

def get_new_auctions_and_analyzing_them(logger, last_api_update):
    TIMEOUT = 3 #in seconds
    cur_page = 0
    total_pages = 1

    while cur_page < total_pages:
        req = requests.get(HYPIXEL_API_AUCTIONS_LINK, params={"page": cur_page}, timeout=TIMEOUT)
        logger.debug(f"Got auctions list page {cur_page} / {total_pages} (0/1 not a bug)")
        if req.status_code != 200:
            logger.warning(f"req for auctions page {cur_page}/{total_pages} (if 0/1 : not a bug) finished with code {req.status_code}")

        req_json = req.json()
        if req_json["success"]:
            total_pages = req_json["totalPages"]

            if last_api_update is None:
                last_api_update = req_json["lastUpdated"]
            elif last_api_update != req_json["lastUpdated"]:
                last_api_update = req_json["lastUpdated"]
                logger.warning(f"lastUpdated changed between pages requests beggining and this page, {cur_page}/{total_pages}")

            for auction in req_json["auctions"]:
                if "bin" in auction and auction["bin"] is True and auction["uuid"] not in Auction.auction_uuid_to_obj: #is a new auction and a bin one
                    auction_attributes, item_attributes = get_useful_data_from_auction(auction)
                    if auction_attributes is not None and item_attributes is not None and auction_attributes["item_count"] > 0:
                        auction_obj = Auction(item=Item(**item_attributes), **auction_attributes)
                        
                        must_be_alert, profitability = auction_obj.calculate_profitability()
                        if must_be_alert:
                            print("------------- Aleeeeeeeeeeert -----------")
                            print(auction["item_name"], profitability, "/viewauction", auction["uuid"])
                            #TODO sending to discord part that it is an alert

        else:
            logger.error(f"req for auctions page {cur_page}/{total_pages} has success = false, json : {req_json}")
        
        cur_page += 1
    return last_api_update

def get_sold_auctions_and_analyzing_them(logger):
    req = requests.get(HYPIXEL_API_ENDED_AUCTIONS_LINK)
    logger.debug("Got ended auctions")
    if req.status_code != 200:
            logger.warning(f"req for ENDED auctions page finished with code {req.status_code}")
    req_json = req.json()
    if req_json["success"]:
        for auction in req_json["auctions"]:
            if auction["auction_id"] in Auction.auction_uuid_to_obj:
                auction_obj = Auction.auction_uuid_to_obj[auction["auction_id"]]
                print("ended", auction_obj)
                sold_auction = SoldAuction(auction_obj)
                sold_auction.sold(auction["price"])

    else:
        logger.error(f"req for ENDED auctions page has success = false, json : {req_json}")

def wait_until_api_refresh(logger, last_api_update):
    OFFICIAL_REFRESH_INTERVALL = 60 #refreshes every minutes
    WAITING_TIME_WHEN_OFFICIAL_REFRESH_INTERVALL_OVERRUNED = 2

    def request_the_last_api_update():
        req = requests.get(HYPIXEL_API_AUCTIONS_LINK)
        logger.debug("Got auctions list for waiting a new api refresh")
        if req.status_code != 200:
                logger.warning(f"req for auctions list when waiting a new api refresh finished with code {req.status_code}")
        req_json = req.json()
        if req_json["success"]:
            return req_json["lastUpdated"]
        else:
            logger.error(f"req for auctions list when waiting a new api refresh = false, json : {req_json}")
            return 0 #error
    
    def do_something_when_waiting(waiting_time):
        logger.debug(f"doing do_something_when_waiting for {waiting_time}")
        time.sleep(waiting_time)
    
    last_updated_got_with_request = request_the_last_api_update()

    while last_updated_got_with_request == last_api_update:
        if last_api_update + OFFICIAL_REFRESH_INTERVALL > time.time() + 2: #if we have more than 2 secs before the official refresh
            do_something_when_waiting(last_api_update + OFFICIAL_REFRESH_INTERVALL - time.time() - 2) #we're waiting until 2 secs before official refresh
        else:
            do_something_when_waiting(WAITING_TIME_WHEN_OFFICIAL_REFRESH_INTERVALL_OVERRUNED)
        
        last_updated_got_with_request = request_the_last_api_update()

    return last_updated_got_with_request #will be the new last_api_update

def main_getting_and_analyzing_api():
    RUNS_BETWEEN_SAVES = 2

    logger = init_a_new_logger("Main API HAM")
    logger.info("main_getting_and_analyzing_api started")
    last_api_update = None
    runs_since_last_save = 0

    while GlobalHAM.run:
        last_api_update = get_new_auctions_and_analyzing_them(logger, last_api_update)
        get_sold_auctions_and_analyzing_them(logger)

        if runs_since_last_save > RUNS_BETWEEN_SAVES:
            save_sold_history()
            runs_since_last_save = 0
        else:
            runs_since_last_save += 1
        
        last_api_update = wait_until_api_refresh(logger, last_api_update)

def listening_to_main_microservices_serv():
    logger = init_a_new_logger("Socket listening HAM")
    logger.info("listening_to_main_microservices_serv started")
    

process_main_getting_and_analyzing_api = threading.Thread(target=main_getting_and_analyzing_api)
process_main_getting_and_analyzing_api.start()
#process_main_getting_and_analyzing_api.join()

process_listening_to_main_microservices_serv = threading.Thread(target=listening_to_main_microservices_serv)
process_listening_to_main_microservices_serv.start()

main_py_file_logger.info("Hypixel Api Microservice finished init")