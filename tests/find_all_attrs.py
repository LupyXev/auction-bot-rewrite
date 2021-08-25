import requests
import base64
import io
import nbt
import json

def print_attr(uuid):
    page, nb_pages = 0, 1
    while page < nb_pages:
        r = requests.get(f"https://api.hypixel.net/skyblock/auctions?page={page}")
        r_json = r.json()
        nb_pages = r_json["totalPages"]

        for auction in r_json["auctions"]:
            if auction["uuid"] == uuid:
                data = auction["item_bytes"]
                dataDecoded = base64.b64decode(data)
                nbt_data = nbt.nbt.NBTFile(fileobj=io.BytesIO(base64.b64decode(data)))
                extras_data = nbt_data["i"][0]["tag"]["ExtraAttributes"]
                print(extras_data.pretty_tree())
                """a = []
                for enchant in extras_data["enchantments"]:
                    print(enchant, extras_data["enchantments"][enchant])"""
                exit()
print_attr("bee8c31add904fa6a5d3faaded158a93")

page, nb_pages = 0, 1
extra_attributes = {}
extra_conserv = []

attr_to_find = ["hot_potato_count", "hotPotatoBonus", "skin", "talisman_enrichment",
    "art_of_war_count", "farming_for_dummies_count"]

while page < nb_pages:
    r = requests.get(f"https://api.hypixel.net/skyblock/auctions?page={page}")
    r_json = r.json()
    nb_pages = r_json["totalPages"]

    for auction in r_json["auctions"]:
        data = auction["item_bytes"]
        dataDecoded = base64.b64decode(data)
        nbt_data = nbt.nbt.NBTFile(fileobj=io.BytesIO(base64.b64decode(data)))
        extras_data = nbt_data["i"][0]["tag"]["ExtraAttributes"]
        """for extra in extras_data:
            if extra not in extra_attributes:
                reponse = None
                while reponse != "n" and reponse != "y":
                    reponse = input(f"{extra} conserv (y/n) ")
                
                if reponse == "n":
                    extra_attributes[extra] = False
                elif reponse == "y":
                    extra_attributes[extra] = True
                    extra_conserv.append(extra)"""
        for attr in attr_to_find:
            if attr in extras_data:
                print("----", attr, "----")
                print(extras_data.pretty_tree())
                attr_to_find.remove(attr)
                print(f"{len(attr_to_find)} restants")
    
    print(page)
    page += 1

print(extra_attributes.values())
print(extra_conserv)

"""TAG_Compound('ExtraAttributes'): {7 Entries}
{
        TAG_Int('hot_potato_count'): 10
        TAG_String('modifier'): fierce
        TAG_String('originTag'): QUICK_CRAFTING
        TAG_String('id'): BLAZE_HELMET
        TAG_Compound('enchantments'): {5 Entries}
        {
                TAG_Int('thorns'): 3
                TAG_Int('protection'): 5
                TAG_Int('respiration'): 3
                TAG_Int('growth'): 5
                TAG_Int('aqua_affinity'): 1
        }
        TAG_String('uuid'): bce9a6c6-f1db-4353-8f41-54a1f04e4406
        TAG_String('timestamp'): 7/15/21 5:58 AM
}
"""