try:
    from hypixel_api_microservices_utils.hypixel_data_objs import *
    from hypixel_api_microservices_utils.logs_obj import init_a_new_logger
except:
    from hypixel_data_objs import *
    from logs_obj import init_a_new_logger

from json import load

ignored_items = ()
try:
    with open("../data/ignored-items.json") as f:
        ignored_items = tuple(load(f))
except:
    with open("data/ignored-items.json") as f:
        ignored_items = tuple(load(f))

logger = init_a_new_logger("HAM Internal microservices commands")

def cmd_ping(args, microservice, sent_from):
    print("heyy")

def cmd_search_item_name(args, microservice, sent_from):
    if not hasattr(microservice, "sender"):
        logger.error("cannot find an item name because microservice obj hasn't a sender attribute")
        return
    sender = microservice.sender
    
    l_dist, found_names = BasicItem.search_item_name(args["item_name"])

    if l_dist > len(args["item_name"]) / 2:
        sender.send_to_a_microservice(sender.EXISTING_REQUEST, sent_from, "search_item_name", {"status": "NOTHING ACCURATE"}, args["request_id"])
        return
    if len(found_names) < 1:
        sender.send_to_a_microservice(sender.EXISTING_REQUEST, sent_from, "search_item_name", {"status": "NOTHING FOUND"}, args["request_id"])
        return
    if len(found_names) > 1:
        sender.send_to_a_microservice(sender.EXISTING_REQUEST, sent_from, "search_item_name", {"status": "MULTIPLE FOUND", "found_names": found_names}, args["request_id"])
        return
    sender.send_to_a_microservice(sender.EXISTING_REQUEST, sent_from, "search_item_name", {"status": "OK", "found_name": found_names[0]}, args["request_id"])

def cmd_get_price_with_search_item_name(args, microservice, sent_from):
    if not hasattr(microservice, "sender"):
        logger.error("cannot find an item name (in cmd_get_price_with_search_name) because microservice obj hasn't a sender attribute")
        return
    sender = microservice.sender
    
    l_dist, found_names = BasicItem.search_item_name(args["item_name"])

    if l_dist > len(args["item_name"]) / 2:
        sender.send_to_a_microservice(sender.EXISTING_REQUEST, sent_from, "get_price_with_search_item_name", {"status": "NOTHING ACCURATE"}, args["request_id"])
        return
    if len(found_names) < 1:
        sender.send_to_a_microservice(sender.EXISTING_REQUEST, sent_from, "get_price_with_search_item_name", {"status": "NOTHING FOUND"}, args["request_id"])
        return
    if len(found_names) > 1:
        sender.send_to_a_microservice(sender.EXISTING_REQUEST, sent_from, "get_price_with_search_item_name", {"status": "MULTIPLE FOUND", "found_names": found_names, "intervall": args["intervall"]}, args["request_id"])
        return
    
    #if we reach here, we had only 1 search result so we can continue with next funct
    args["item_name"] = found_names[0]
    cmd_get_price_with_correct_name(args, microservice, sent_from)

def cmd_get_price_with_correct_name(args, microservice, sent_from):
    if not hasattr(microservice, "sender"):
        logger.error("microservice hasn't sender attr for cmd_get_price_with_correct_name")
        return

    item_id = BasicItem.ALIAS_ID_BY_LOWCASE_NAME[args["item_name"].lower()]

    if item_id in ignored_items:
        microservice.sender.send_to_a_microservice(microservice.sender.EXISTING_REQUEST, sent_from, "get_price_with_correct_name", {"status": "IGNORED ITEM"}, args["request_id"])
        return

    intervall = args["intervall"]
    best_basic_item = [None, 0] #obj, sold_hist_lenght_in_
    if item_id in BasicItem.basicitem_dict:
        for by_tier in BasicItem.basicitem_dict[item_id].values():
            for basic_item in by_tier.values():
                sold_hist_lenght = len(basic_item.estimated_price_sold_hist.get_for_an_intervall(intervall))
                if sold_hist_lenght > best_basic_item[1]:
                    best_basic_item = [basic_item, sold_hist_lenght]
    
    basic_item = best_basic_item[0]
    if basic_item is None:
        #no accurate sold hist found
        microservice.sender.send_to_a_microservice(microservice.sender.EXISTING_REQUEST, sent_from, "get_price_with_correct_name", {"status": "NO ACCURATE SOLD HIST"}, args["request_id"])
        return
    
    median_price, sold_hist_lenght = basic_item.estimated_price_sold_hist.get_median(intervall, return_sold_hist_lenght_used=True)
    to_send_args = {
        "status": "OK",
        "intervall": intervall,
        "median_price": median_price,
        "sold_hist_lenght": sold_hist_lenght,
        "dungeon_level": basic_item.dungeon_level,
        "tier": basic_item.tier.tier_id,
        "item_name": args["item_name"],
        "item_id": item_id
    }
    microservice.sender.send_to_a_microservice(microservice.sender.EXISTING_REQUEST, sent_from, "get_price_with_correct_name", to_send_args, args["request_id"])

text_to_command = {
    ">ping": cmd_ping,
    ">search_item_name": cmd_search_item_name,
    ">get_price_with_search_item_name": cmd_get_price_with_search_item_name,
    ">get_price_with_correct_name": cmd_get_price_with_correct_name
}