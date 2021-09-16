try:
    from hypixel_api_microservices_utils.hypixel_data_objs import *
except:
    from hypixel_data_objs import *

def cmd_ping(args, microservice):
    print("heyy")

def get_price_with_name(args, microservice): #not the command
    if not hasattr(microservice, "sender"):
        return None
    better_basic_item = [None, 0] #obj, sold history lenght
    reforge_dict = BasicItem.basicitem_dict[args["item_name"]]

def cmd_get_price_with_name(args, microservice):
    price = get_price_with_name(args, microservice)


text_to_command = {
    "ping": cmd_ping,
    "get_price_with_item_name": cmd_get_price_with_name
}