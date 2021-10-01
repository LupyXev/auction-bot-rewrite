from hypixel_api_microservices_utils.hypixel_data_objs import *
from hypixel_api_microservices_utils.logs_obj import init_a_new_logger
from hypixel_api_microservices_utils.others_objs import GlobalHAM
from hypixel_api_microservices_utils.sql_utils import save_sold_history, load_sold_history, save_stats, load_stats
import hypixel_api_microservices_utils.internal_microservices_commands as internal_microservices_commands

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
import socket
from microservices_utils.objs import MicroserviceReceiver, MicroserviceSender, Microservice
from json import load

HYPIXEL_API_SKYBLOCK_LINK = "https://api.hypixel.net/skyblock/"
HYPIXEL_API_AUCTIONS_LINK = HYPIXEL_API_SKYBLOCK_LINK + "auctions"
HYPIXEL_API_ENDED_AUCTIONS_LINK = HYPIXEL_API_SKYBLOCK_LINK + "auctions_ended"
MICROSERVICE_NAME = "hypixel_api_analysis"
MICROSERVICE_PREFIX = "H"

microservice = Microservice(MICROSERVICE_NAME, MICROSERVICE_PREFIX, {})
sender = MicroserviceSender(microservice, init_a_new_logger("MicroserviceSender HAM"))

sender.send_to_a_microservice(sender.FIRST_REQUEST, "discord_bot", "send", {"channel_id": 811605424935403560, "content": "microservice hypixel api lancé"})
#sender.send_to_a_microservice(sender.FIRST_REQUEST, "discord_bot", "send", {"channel_id": 811605424935403560, "content": "test"})

ignored_items = ()
with open("data/ignored-items.json") as f:
    ignored_items = tuple(load(f))

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
    basicitem = BasicItem.get_basicitem(**basicitem_attributes)
    if basicitem is None:
        #the basic item might had an alias error
        #we add the item's name to show the missing alias
        if basicitem_attributes["item_id"] in BasicItem.ITEM_IDS_NOT_IN_ALIAS_TO_SEND_TO_DISCORD and BasicItem.ITEM_IDS_NOT_IN_ALIAS_TO_SEND_TO_DISCORD[basicitem_attributes["item_id"]] is None: #if the last added have no name
            BasicItem.ITEM_IDS_NOT_IN_ALIAS_TO_SEND_TO_DISCORD[basicitem_attributes["item_id"]] = auction["item_name"]
        return None, None

    if basicitem.can_be_drop_enchanted:
        enchants_type = EnchantType.ENCHANTED_DUNGEON_ITEM_TYPE
    elif basicitem.item_id == "ENCHANTED_BOOK":
        enchants_type = EnchantType.ENCHANTED_BOOK_TYPE
    else:
        enchants_type = EnchantType.CLASSIC_TYPE
    if "enchantments" in extra_attributes: 
        enchants = []
        for enchant in extra_attributes["enchantments"]:
            enchants.append(EnchantType.get_enchant_type(enchant, enchants_type).get_enchant(extra_attributes["enchantments"][enchant].value))
        enchants = tuple(enchants)
    else:
        enchants = ()

    for attr in extra_attributes:
        if attr in AdditionalAttributeSpecialized.ATTRIBUTES_NAME_FOR_THIS_CLASS or attr in AdditionalAttributeUnspecialized.ATTRIBUTES_NAME_FOR_THIS_CLASS:
            #logger.debug(f"Item {auction['item_name']} skipped because of an additionnal attribute")
            return None, None


    item_attributes = {"item_name": auction["item_name"], "basicitem": basicitem, "reforge": reforge, "enchants": enchants, "runes": runes}
    return auction_attributes, item_attributes

def get_new_auctions_and_analyzing_them(logger, last_api_update, cur_run):
    TIMEOUT = 3 #in seconds
    cur_page = 0
    total_pages = 1
    first_last_api_update = None

    while cur_page < total_pages:
        req = requests.get(HYPIXEL_API_AUCTIONS_LINK, params={"page": cur_page}, timeout=TIMEOUT)
        logger.debug(f"Run {cur_run}: Got auctions list page {cur_page} / {total_pages} (0/1 not a bug)")
        if req.status_code != 200:
            logger.warning(f"req for auctions page {cur_page}/{total_pages} (if 0/1 : not a bug) finished with code {req.status_code}")

        req_json = req.json()
        if req_json["success"]:
            total_pages = req_json["totalPages"]

            if last_api_update is None:
                last_api_update = req_json["lastUpdated"] / 1000
            elif last_api_update != req_json["lastUpdated"] / 1000:
                last_api_update = req_json["lastUpdated"] / 1000
                logger.warning(f"lastUpdated changed between pages requests beggining and this page, {cur_page}/{total_pages}")
            if first_last_api_update is None:
                first_last_api_update = req_json["lastUpdated"] / 1000

            for auction in req_json["auctions"]:
                if "bin" in auction and auction["bin"] is True and auction["uuid"] not in Auction.auction_uuid_to_obj and auction["item_name"] != "null" : #is a new auction and a bin one
                    auction_attributes, item_attributes = get_useful_data_from_auction(auction)
                    if auction_attributes is not None and item_attributes is not None and auction_attributes["item_count"] > 0 and\
                        item_attributes["basicitem"].item_id not in ignored_items:
                        #we can handle this auction/item
                        auction_obj = Auction(item=Item(**item_attributes), **auction_attributes)
                        
                        if cur_run > 0:
                            Statistics.dict["total_bin_auctions_scanned"] += 1
                            Statistics.dict["total_bin_auctions_prices"] += auction_obj.starting_bid
                        
                        must_be_alert, absolute_profitability, relative_profitability, trust_rate = auction_obj.calculate_profitability(cur_run, microservice)
                        if must_be_alert and cur_run > 0 and auction_obj.item.estimation.item_only[0] != None:
                            
                            full_estimation = auction_obj.item.estimation

                            item_data = {
                                "name": auction_obj.item.item_name,
                                "tier": auction_obj.item.basic.tier.tier_id,
                                "item_only": {"estimation": full_estimation.item_only[0], "sold_amount": full_estimation.item_only[3]},
                                "enchants_type": None
                            }
                            
                            reforge = auction_obj.item.reforge
                            if reforge is not None:
                                item_data["reforge"] = {"name": reforge.reforge_id, "estimation": full_estimation.reforge[0], "sold_amount": full_estimation.reforge[3]}
                            
                            enchants = auction_obj.item.enchants
                            if len(enchants) > 0:
                                item_data["enchants"] = []
                                item_data["enchants_type"] = enchants[0].basic.enchant_type
                                for enchant in enchants:
                                    enchant_estimation = full_estimation.enchants[enchant]
                                    item_data["enchants"].append({"name": f"{enchant.basic.enchant_type_id} {enchant.level}", "estimation": enchant_estimation[0]})
                            
                            runes = auction_obj.item.runes
                            if len(runes) > 0:
                                item_data["runes"] = []
                                for rune in runes:
                                    rune_estimation = full_estimation.runes[rune]
                                    item_data["runes"].append({"name": f"{rune.basic.rune_type_id} {rune.level}", "estimation": rune_estimation[0], "sold_amount": full_estimation.reforge[3]})

                            if cur_run > 0:
                                Statistics.dict["total_estimated_profit"] += absolute_profitability
                                Statistics.dict["total_advices"] += 1
                                Statistics.dict["total_advices_prices"] += auction_obj.starting_bid

                            sender.send_to_a_microservice(sender.FIRST_REQUEST, "discord_bot", "stonks_alert", {
                                "intervalls_used": full_estimation.intervalls_used,
                                "absolute_profitability": absolute_profitability, 
                                "relative_profitability": relative_profitability,
                                "full_estimation": full_estimation.total,
                                "buy_price": auction_obj.starting_bid,
                                "lowest_bins": auction_obj.item.basic.get_lowests_bins(),
                                "potential_resell_price": full_estimation.total,
                                "item_data": item_data,
                                "seller_uuid": auction_obj.seller_uuid,
                                "auction_uuid": auction_obj.uuid,
                                "trust_rate": trust_rate
                                })

        else:
            logger.error(f"req for auctions page {cur_page}/{total_pages} has success = false, json : {req_json}")
        
        cur_page += 1
    return first_last_api_update

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
            return req_json["lastUpdated"] / 1000
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

def full_cleanup(logger):
    logger.info("Starting cleanup")
    Reforge.cleanup()
    EnchantType.cleanup()
    RuneType.cleanup()
    BasicItem.cleanup()

def main_getting_and_analyzing_api():
    RUNS_BETWEEN_SAVES = 2
    RUNS_BETWEEN_CLEANUPS = 20

    logger = init_a_new_logger("Main API HAM")
    logger.info("main_getting_and_analyzing_api started")
    last_api_update = None
    runs_since_last_save, runs_since_last_cleanup = 0, 0
    cur_run = 0
    load_sold_history()
    load_stats()

    while GlobalHAM.run:
        sender.send_to_a_microservice(sender.FIRST_REQUEST, "discord_bot", "cur_run_number", {"run_number": cur_run})
        last_api_update = get_new_auctions_and_analyzing_them(logger, last_api_update, cur_run)
        get_sold_auctions_and_analyzing_them(logger)

        #to send missing alias
        for item_id, item_name in BasicItem.ITEM_IDS_NOT_IN_ALIAS_TO_SEND_TO_DISCORD.items():
            sender.send_to_a_microservice(sender.FIRST_REQUEST, "discord_bot", "missing_alias", {"item_id": item_id, "item_name": item_name})
            BasicItem.ITEM_IDS_NOT_IN_ALIAS_SENT_TO_DISCORD.append(item_id)
        BasicItem.ITEM_IDS_NOT_IN_ALIAS_TO_SEND_TO_DISCORD = {} #clear everything bc we've already processed everything

        if runs_since_last_save >= RUNS_BETWEEN_SAVES:
            save_sold_history()
            save_stats()
            runs_since_last_save = 0
        else:
            runs_since_last_save += 1
        
        if runs_since_last_cleanup >= RUNS_BETWEEN_CLEANUPS:
            full_cleanup(logger)
            runs_since_last_cleanup = 0
        else:
            runs_since_last_cleanup += 1
        
        last_api_update = wait_until_api_refresh(logger, last_api_update)

        cur_run += 1

def listening_to_main_microservices_serv():
    logger = init_a_new_logger("Socket listening HAM")
    logger.info("listening_to_main_microservices_serv started")
    receiver = MicroserviceReceiver(microservice, logger)
    logger.info(f"new MicroserviceReceiver created for {microservice.name} microservice")
    time.sleep(0.1)
    while GlobalHAM.run:
        if not receiver.connection_alive:
            time.sleep(1)
        while receiver.connection_alive:
            req = receiver.listen()
            if req is None:
                break #connection closed, not alive anymore
            if req["command"] in internal_microservices_commands.text_to_command:
                internal_microservices_commands.text_to_command[req["command"]](req["args"], microservice, req["sender"])
            else:
                logger.error(f"Got a request with a command not in text_to_command : {req}")

process_main_getting_and_analyzing_api = threading.Thread(target=main_getting_and_analyzing_api)
process_main_getting_and_analyzing_api.start()

process_listening_to_main_microservices_serv = threading.Thread(target=listening_to_main_microservices_serv)
process_listening_to_main_microservices_serv.start()

main_py_file_logger.info("Hypixel Api Microservice finished init")