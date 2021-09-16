
import os
import time
from datetime import datetime
import logging
import logging.handlers

r_file_handler = logging.handlers.RotatingFileHandler(
    filename='discord_bot.log', 
    mode='a',
    maxBytes=5*1024*1024,
    backupCount=1,
    encoding="utf-8",
    delay=0
)
r_file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
r_file_handler.setFormatter(formatter)

logger = logging.getLogger('root')
logger.setLevel(logging.INFO)
logger.addHandler(r_file_handler)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


#logging.basicConfig(level=logging.INFO, handlers=[r_file_handler])

logger.info(f"--------| {datetime.fromtimestamp(time.time())} Start |--------")

def log(content):
    print(f"{content}")
    logger.info(f"{datetime.fromtimestamp(time.time())} : {content}")

try:
    TOKEN = os.environ["TOKEN"]
    is_nightly = False
    log("normal mode")
except:
    TOKEN = "ODUxMDQzNTA2NjU5MjYyNDg0.YLyiBw._wW_KwuGd8FUMUIS15dVx3Xs3NA"
    log("Nightly mode")
    is_nightly = True

    
    
import psutil
process = psutil.Process(os.getpid())
log(f"avant imports {process.memory_info().rss / 1024 ** 2}")

import requests
import json
import discord
import asyncio
import aiohttp
import io
import nbt
import base64
import gzip
import sqlite3
from discord.ext import tasks

from math_fonctions import *
import sys
import dbtools
import data_utils as du

log(f"après imports {process.memory_info().rss / 1024 ** 2}")
# from dotenv import load_dotenv

# load_dotenv()
url = "https://api.hypixel.net/skyblock/"

TOKEN_HYPIXEL = "251927be-35e3-4898-a435-25e1eb5956d3"
hypixel_token_used_history = [] #la liste des timestamps
TOKEN_ITEMS_API = "Y1ajHdYWmFgYo1gbdAj5OkBRQrNz5EzVi48OIgwv"
DATABASE_URL = "ec2-54-155-226-153.eu-west-1.compute.amazonaws.com"
prefix = "ah$"
lang = "fr"
urlApiUuidToPseudo = "https://minecraft-api.com/api/pseudo/"
lienDInvitation = "https://discord.com/oauth2/authorize?client_id=811604371073794089&scope=bot&permissions=268954696"

with open("credentials.json") as f:
    credentials = json.load(f)

texteDefaultActivity = "prefix : ah$"
defaultActivity = discord.Game(texteDefaultActivity)
discordStatus = discord.Status.online

blacklisted_items = ("SPOOKY_PIE", "ONYX", "NOPE_THE_FISH", "BAT_THE_FISH", "MAXOR_THE_FISH", "GIFT_THE_FISH", "SHRIMP_THE_FISH", "GOLDOR_THE_FISH", "CANDY_THE_FISH", "SNOWFLAKE_THE_FISH",
                     "STORM_THE_FISH", "CLUCK_THE_FISH", "EGG_THE_FISH", "EXPERIMENT_THE_FISH", "MIDAS_STAFF", "MIDAS_SWORD", "DUNGEON_LORE_PAPER","DUNGEON_STONE", "ASPECT_OF_THE_VOID","PET_SKIN_BLACK_CAT_IVORY", "NEW_YEAR_CAKE")

messagesContent = {
    "help": {"en": '''__Command's list :__
    - **ping**: bot's latency
    - **auctions**: commands about auctions
        - auctions number : auction's number
            ''',
             "fr": '''__Liste des commandes :__
    - **ping**: Latence du bot
    - online-time : Depuis combien de temps le bot est online
    - errors : le pourcentage d'erreur
    - number : Le nombre d'auctions
    - **bin** : Commandes pour les bins
        -> bin **price** *Nom d'un item* : Commande pour connaître le prix moyen de vente d'un item
        -> bin **list** : La liste des items pour lesquels le prix moyen est disponible
            '''},
    "argument_necessaire": {"en": ":x: An argument is needed", "fr": ":x: Un argument est nécessaire"},

}
listeDesEmojis = [
        "1️⃣",
        "2️⃣",
        "3️⃣",
        "4️⃣",
        "5️⃣",
        "6️⃣",
        "7️⃣",
        "8️⃣",
        "9️⃣",
        "🔟",
        "🇦",
        "🇧",
        "🇨",
        "🇩",
        "🇪",
        "🇫",
        "🇬",
        "🇭"
]
indexDUnEmoji = {
    "1️⃣": 1,
    "2️⃣": 2,
    "3️⃣": 3,
    "4️⃣": 4,
    "5️⃣": 5,
    "6️⃣": 6,
    "7️⃣": 7,
    "8️⃣": 8,
    "9️⃣": 9,
    "🔟": 10,
    "🇦": 11,
    "🇧": 12,
    "🇨": 13,
    "🇩": 14,
    "🇪": 15,
    "🇫": 16,
    "🇬": 17,
    "🇭": 18
}
tiers_reforgeables = {"COMMON": 1,
                      "UNCOMMON": 2,
                      "RARE": 4,
                      "EPIC": 10,
                      "LEGENDARY": 20,
                      "MYTHIC": 40,
                      "SPECIAL": 100,
                      "VERY_SPECIAL": 200
                      }
couplesItemsEtRarityToIgnore = {"BASE_GRIFFIN_UPGRADE_STONE": ("UNCOMMON", "RARE", "EPIC", "LEGENDARY"),
                                "GRIFFIN_UPGRADE_STONE_RARE": ("EPIC", "LEGENDARY"),
                                "GRIFFIN_UPGRADE_STONE_UNCOMMON": ("RARE", "EPIC", "LEGENDARY"),
                                "GRIFFIN_UPGRADE_STONE_EPIC": ("LEGENDARY")}
nuances = (0xffff00, 0xff8c1a, 0xff4d94, 0xcc66ff, 0x1a75ff)

events_list = ("New Year Celebration", "Spooky Festival", "Winter Island")

images_percentage = ("https://cdn.discordapp.com/attachments/811611272251703357/858393696809517066/0.png",
                     "https://cdn.discordapp.com/attachments/811611272251703357/858393698470330408/10.png",
                     "https://cdn.discordapp.com/attachments/811611272251703357/858393700086185984/20.png",
                     "https://cdn.discordapp.com/attachments/811611272251703357/858393701699813386/30.png",
                     "https://cdn.discordapp.com/attachments/811611272251703357/858393703302955038/40.png",
                     "https://cdn.discordapp.com/attachments/811611272251703357/858393704889188362/50.png",
                     "https://cdn.discordapp.com/attachments/811611272251703357/858393706398744617/60.png",
                     "https://cdn.discordapp.com/attachments/811611272251703357/858393708130598932/70.png",
                     "https://cdn.discordapp.com/attachments/811611272251703357/858393709959970816/80.png",
                     "https://cdn.discordapp.com/attachments/811611272251703357/858393773095780382/90.png",
                     "https://cdn.discordapp.com/attachments/811611272251703357/858393695123538001/100.png")
index_de_stockage_to_type = ("Item", "Tier", "Rarity upgrade", "Dungeon level", "Reforge", "Enchantments", "Rune", "Additional data")

#---- les commandes ----
async def cmd_stats(args, message):
    #global bot_stats
    await message.channel.send(embed=await generer_embed(message,
                                                   "📈" + get_traduction_message("stats titre", message.author.id),
                                                   get_traduction_message("stats contenu", message.author.id),
                                                   fields=[[get_traduction_message('stats profit', message.author.id), f"{jolis_chiffres(bot_stats['profit'])}", False],
                                                           [get_traduction_message('stats advices amount', message.author.id), f"{jolis_chiffres(bot_stats['advise amount'])}", True],
                                                           [get_traduction_message('stats advices price amount', message.author.id), f"{jolis_chiffres(bot_stats['advise price amount'])}", False],
                                                           [get_traduction_message('stats commandes', message.author.id), f"{jolis_chiffres(bot_stats['commandes'])}", False],
                                                           [get_traduction_message('stats auctions scanned', message.author.id), f"{jolis_chiffres(bot_stats['auctions scanned'])}", True],
                                                           [get_traduction_message('stats auctions scanned price amount', message.author.id), f"{jolis_chiffres(bot_stats['auctions scanned prices amount'])}", False]],
                                                   ))

async def cmd_help(args, message):
    global helps
    try:
        lang_actu = playersData[str(message.author.id)]["lang"]
    except:
        lang_actu = "en"
    if len(args) < 2:
        fields = []
        content = ""
        content += f"\n`ping`: {helps['ping']['desc'][lang_actu]}"
        content += f"\n`config`: {helps['config']['desc'][lang_actu]}"
        content += f"\n`stats`: {helps['stats']['desc'][lang_actu]}"
        content += f"\n`uptime`: {helps['uptime']['desc'][lang_actu]}"
        content += f"\n`donators`: {helps['donators']['desc'][lang_actu]}"
        fields.append([f"🛠️ {get_traduction_message('utilitaire', message.author.id)}", content, False])

        content = ""
        content += f"\n`events`: {helps['events']['desc'][lang_actu]}"
        content += f"\n`price`: {helps['price']['desc'][lang_actu]}"
        fields.append([f"📃 {get_traduction_message('infos-skyblock', message.author.id)}", content, False])
        await message.channel.send(embed=await generer_embed(message, get_traduction_message('aide', message.author.id), get_traduction_message("commandes disponibles", message.author.id), fields=fields))
    else:
        if args[1] in helps:
            await message.channel.send(embed=await generer_embed(message, f"ah${args[1]}", f"{helps[args[1]]['desc'][lang_actu]}", fields=[[get_traduction_message("exemple", message.author.id), f"{helps[args[1]]['example'][lang_actu]}", False]]))
        else:
            await message.channel.send(get_traduction_message("commande inconnue", message.author.id))

async def cmd_ping(args, message):
    envoi = await message.channel.send(content="ping")
    dateEnvoi = (envoi.created_at).timestamp()
    await envoi.edit(content=f"pong {round((get_current_utc_timestamp() - dateEnvoi) * 1000)}ms")


'''async def cmd_number(args, message):
    number, lastUpdate = get_auction_number()
    await message.channel.send(
        content=f"**{number}** auctions are online\nLast update : {datetime.fromtimestamp(lastUpdate / 1000)} (Paris)")'''

async def cmd_online_time(args, message):
    await message.channel.send(
        get_traduction_message("temps depuis allumage", message.author.id, [datetime.fromtimestamp(timestampDemarrage)]))

async def cmd_price(args, message):
    message_splitted_by_search_and_duration = message.content.split(" for ")
    if len(message_splitted_by_search_and_duration) > 2:
        message_splitted_by_search_and_duration[0] = " for ".join(message_splitted_by_search_and_duration[:-1]) #si il y a un for dans le nom de l'item

    recherche = message_splitted_by_search_and_duration[0][len(args[0])+1:] #juste le nom de l'item

    if len(message_splitted_by_search_and_duration) > 1: #si on a une durée de demandée
        duration = joli_heure_to_timestamp(message_splitted_by_search_and_duration[1])
    else:
        duration = 7200

    result = await search_algorithm(recherche, hypixelAlias, 15)

    if result[0][1] < 5:  # si on a pas trouvé d'item correspondant aux mots-clés
        messageItemsPossibles = ""
        for i in result:
            messageItemsPossibles += f" - {hypixelAlias[i[0]][0]}\n"

        await message.channel.send(embed=await generer_embed(message,
                            get_traduction_message("item non trouve titre", message.author.id),
                            get_traduction_message("item non trouve desc", message.author.id),
                            fields=[(get_traduction_message("items possibles", message.author.id), messageItemsPossibles, False)],
                            thumbnail="https://static.wikia.nocookie.net/hypixel-skyblock/images/c/cc/Barrier.png/revision/latest?cb=20191018090137"))
        return
    elif result[0][1] - result[1][1] < 2: #si des resultats sont trop proches
        i = 0
        while i < len(result) and result[0][1] - result[i][1] < 3:
            i += 1
        itemsHesitation = result[:i+1]
        messageReponse = await message.channel.send(embed=await generer_embed(message,
                                                             get_traduction_message("hesitation item", message.author.id),
                                                             get_traduction_message("plusieurs items trouves", message.author.id),
                                                             fields=[(hypixelAlias[itemsHesitation[i][0]][0], f"{get_traduction_message('reagir avec', message.author.id)} {listeDesEmojis[i]}", False) for i in range(len(itemsHesitation))],
                                                             thumbnail="https://cdn.discordapp.com/attachments/811611272251703357/833036031413714954/question-mark-1750942_1280.png"))
        global reactionToInteractWith
        reactionToInteractWith[(messageReponse.id, message.author.id)] = (price_reaction, {"recherche_possible": [i[0] for i in itemsHesitation], "duration": duration})
        for i in range(len(itemsHesitation)):
            await messageReponse.add_reaction(listeDesEmojis[i])
        return

    await cmd_price_step2(result[0][0], message, message.author.id, duration)

async def cmd_price_step2(idItem, message, author_id, duration):
    aEnvoyer = ""
    nom_avec_tiers_et_stars = []
    for tier in range(1, len(tier_to_index)+1):
        for star in range(11):
            nom_avec_tiers_et_stars.append(f"{tier}T{star}S{idItem}")

    tier_le_plus_reference = [None, 0] #le nom avec le tier, la quantité

    for nomActu in nom_avec_tiers_et_stars:

        if nomActu in hypixelDataPrices:

            qtteActu = len(await recuperer_uniquement_donnee_selon_intervalle_de_temps(hypixelDataPrices[nomActu], round(time.time() - duration))) #pour compter le nombre de références de ce tier

            if qtteActu > tier_le_plus_reference[1]:
                tier_le_plus_reference = [nomActu, qtteActu]

    if tier_le_plus_reference[0] != None:

        if hypixelDataPrices[tier_le_plus_reference[0]] != []:
            #aEnvoyer += f"Le prix médian de vente de *({}*) est de **"
            donnees_selon_intervalle = await recuperer_uniquement_donnee_selon_intervalle_de_temps(hypixelDataPrices[tier_le_plus_reference[0]], round(get_current_utc_timestamp()) - duration)
            if len(donnees_selon_intervalle) > 0:
                '''aEnvoyer += get_traduction_message("prix median ah$price 1", author_id, [
                    f"{hypixelAlias[idItem][0]}{starsList[int(tier_le_plus_reference[0][2])]}",
                    str(index_to_tier[int(tier_le_plus_reference[0][0])])])'''

                medianeData = await trouver_mediane(donnees_selon_intervalle, 1)
                #aEnvoyer += jolis_chiffres(medianeData)
                #aEnvoyer += get_traduction_message("prix median ah$price 2", author_id, [jolis_chiffres(len(donnees_selon_intervalle)), joli_heure(duration)])
                if duration > 604800:
                    aEnvoyer += get_traduction_message("limitation donnees price", author_id)

                await message.channel.send(embed=await generer_embed(None,
                                                                     f"{hypixelAlias[idItem][0]}{starsList[int(tier_le_plus_reference[0][2])]}",
                                                                     aEnvoyer,
                                                                     fields=[["Tier", f"*{str(index_to_tier[int(tier_le_plus_reference[0][0])])}*", False],
                                                                             ["Intervall used", f"the last __{joli_heure(duration)}__", False],
                                                                             ["Price", f"**{jolis_chiffres(medianeData)}**", True],
                                                                             ["Sold amount", jolis_chiffres(len(donnees_selon_intervalle)), True]],
                                                                     thumbnail=f"https://sky.lea.moe/item/{tier_le_plus_reference[0][4:]}"))
            else:
                aEnvoyer += get_traduction_message("pas de prix trouves", idItem, [joli_heure(duration)])
                if duration > 604_800:
                    aEnvoyer += get_traduction_message("limitation donnees price", author_id)
                #await message.channel.send(content=aEnvoyer)
                await message.channel.send(embed=await generer_embed(None,
                                                                     f"{hypixelAlias[idItem][0]}",
                                                                     aEnvoyer,
                                                                     thumbnail='https://media.discordapp.net/attachments/811611272251703357/861271094458712064/error_v2.webp?width=677&height=676'))
    else:
        # log(hypixelDataPrices)
        #await message.channel.send(
        #    content=get_traduction_message("aucune donnee sur prix item", author_id, [idItem]))
        aEnvoyer = get_traduction_message("pas de prix trouves", idItem, [joli_heure(duration)])
        if duration > 86400:
            aEnvoyer += get_traduction_message("limitation donnees price", author_id)

        await message.channel.send(embed=await generer_embed(None,
                                                             f"{hypixelAlias[idItem][0]}",
                                                             aEnvoyer,
                                                             thumbnail='https://media.discordapp.net/attachments/811611272251703357/861271094458712064/error_v2.webp?width=677&height=676'))


async def cmd_search(args, message):
    recherche = " ".join(args[1:])
    result = await search_algorithm(recherche, hypixelAlias, 10)
    if result[0][1] > 5 and result[0][1] - result[1][1] > 2:  # si on est sûr d'avoir trouvé le bon item
        await message.channel.send(content=get_traduction_message("search resultat sur", message.author.id, [result[0][0]]))
    else:
        await message.channel.send(content=get_traduction_message("search resultat non sur", message.author.id, [result]))

async def cmd_next_events(args, message):
    events_a_envoyer = refresh_events()
    tab_events = [[i[0], f"Coming in **{joli_heure(i[1] - time.time())}** (until {datetime.fromtimestamp(i[1])} UTC+0)", False] for i in events_a_envoyer.items()]
    await message.channel.send(embed=await generer_embed(message,
                                                   get_traduction_message("titre prochains events", message.author.id),
                                                   get_traduction_message("contenu prochains events", message.author.id),
                                                   fields=tab_events
                                                   ))
async def cmd_current_events(args, message):
    events_a_envoyer = current_events(events_timings_data, False)
    tab_events = [[i[0], f"End in **{joli_heure(i[1] - time.time())}** (until {datetime.fromtimestamp(i[1])} UTC+0)", False] for i in events_a_envoyer]
    if len(tab_events) < 1:
        tab_events = [[get_traduction_message("aucun current event", message.author.id), ":x:", False]]
    await message.channel.send(embed=await generer_embed(message,
                                                         get_traduction_message("titre current events",
                                                                                message.author.id),
                                                         get_traduction_message("contenu current events",
                                                                                message.author.id),
                                                         fields=tab_events
                                                         ))
async def cmd_events(args, message):
    events_en_cours = current_events(events_timings_data, False)
    events_coming = refresh_events()

    try:
        if args[1] == "patate":
            events_en_cours = [["Spooky Festival", 1623420655]]
    except:
        pass

    tab_events_coming = [
        [i[0], f"Coming in **{joli_heure(i[1] - time.time())}** (until {datetime.fromtimestamp(i[1])} UTC+0)", False]
        for i in events_coming.items()]
    tab_a_envoyer = []

    for i in range(len(events_list)):
        event_en_cours = False
        for event in events_en_cours:
            if event[0] == events_list[i]:
                event_en_cours = True
                tab_a_envoyer.append([event[0], f"**__<a:loading:852914260341817384> Underway !__**\nEnds in **{joli_heure(event[1] - time.time())}** (until {datetime.fromtimestamp(event[1])} UTC+0)", False])
        if not event_en_cours:
            tab_a_envoyer.append(tab_events_coming[i])

    await message.channel.send(embed=await generer_embed(message,
                                                         get_traduction_message("titre current events",
                                                                                message.author.id),
                                                         get_traduction_message("contenu current events",
                                                                                message.author.id),
                                                         fields=tab_a_envoyer
                                                         ))

async def cmd_config_generic(args, message):
    if len(args) < 2:
        await message.channel.send(get_traduction_message("renseigner mode config", message.author.id))
    elif args[1] == "me":
        await cmd_config_me(args, message)
    elif args[1] == "server":
        await cmd_config_server(args, message)
    else:
        await message.channel.send(get_traduction_message("renseigner mode config", message.author.id))

async def cmd_config_me(args, message):
    global playersData
    userLang = None
    if str(message.author.id) in playersData:
        if "lang" in playersData[str(message.author.id)]:
            userLang = playersData[str(message.author.id)]["lang"]
    envoi = await message.channel.send(embed=await generer_embed(message,
                                                                 get_traduction_message("configuration compte perso titre", message.author.id),
                                                                 get_traduction_message("configuration compte perso description", message.author.id),
                                                                 fields=[
                                                                     [get_traduction_message("langue actu", message.author.id),
                                                                      f"{userLang}\n {get_traduction_message('choisir langue', message.author.id)}",
                                                                      False]]))
    await envoi.add_reaction("🇬🇧")
    await envoi.add_reaction("🇫🇷")
    reactionToInteractWith[(envoi.id, message.author.id)] = (modifier_config_perso_reaction, message.author.id)

async def modifier_config_perso_reaction(message, reaction, donneesAdditionnelles, user_id):
    global playersData, playersDataModified
    if str(donneesAdditionnelles) not in playersData:
        playersData[str(donneesAdditionnelles)] = {}
    if reaction.emoji == "🇫🇷":
        playersData[str(donneesAdditionnelles)]["lang"] = "fr"
        await message.channel.send("Langue française définie")
        playersDataModified = True
    elif reaction.emoji == "🇬🇧":
        playersData[str(donneesAdditionnelles)]["lang"] = "en"
        await message.channel.send("English language has been chosen")
        playersDataModified = True

async def cmd_config_server(args, message):
    authorized = False
    for r in message.author.roles:
        if r.permissions.administrator:
            authorized = True
    if authorized:
        channelStonks = None
        rolesPingStonks = None
        if str(message.guild.id) in guildsData:
            if "channelsStonks" in guildsData[str(message.guild.id)]:
                channelStonksList = guildsData[str(message.guild.id)]["channelsStonks"]
                channelStonks = ""
                for i in channelStonksList:
                    channelStonks += f"{message.guild.get_channel(i[0]).mention} : min {jolis_chiffres(i[1])} profit\n"
            if "rolesPingStonks" in guildsData[str(message.guild.id)]:
                rolesPingStonksList = guildsData[str(message.guild.id)]["rolesPingStonks"]
                rolesPingStonks = ""
                for i in rolesPingStonksList:
                    rolesPingStonks += f"{message.guild.get_role(i[0]).mention} : {get_traduction_message('profit superieur', message.author.id)} {jolis_chiffres(i[1])}\n"
        envoi = await message.channel.send(embed=await generer_embed(message,
                                                         get_traduction_message("config serveur title", message.author.id),
                                                         get_traduction_message("config serveur description", message.author.id),
                                   fields=[
                                    [get_traduction_message('channel stonks actu', message.author.id), f"{channelStonks}\n{get_traduction_message('pour modif cliquer sur', message.author.id)} :one:", False],
                                    [get_traduction_message('roles ping stonks actu', message.author.id), f"{rolesPingStonks} \n{get_traduction_message('pour modif cliquer sur', message.author.id)} :two:", False]]))
        await envoi.add_reaction(listeDesEmojis[0])
        await envoi.add_reaction(listeDesEmojis[1])
        reactionToInteractWith[(envoi.id, message.author.id)] = (modifier_config_reaction, message.author.id)
    else:
        await message.channel.send(content=get_traduction_message('autorisation refusee admin', message.author.id))

async def modifier_config_reaction(message, reaction, donneesAdditionnelles, user_id):
    if str(message.guild.id) not in guildsData:
        guildsData[str(message.guild.id)] = {}

    if reaction.emoji == listeDesEmojis[0]:
        await message.channel.send(get_traduction_message("explications envoi channel stonks v2", donneesAdditionnelles))
        guildsData[str(message.guild.id)]["channelsStonks"] = []
        messageToInteractWith[(message.channel.id, donneesAdditionnelles)] = (modifier_channel_stonks_message, donneesAdditionnelles)
    elif reaction.emoji == listeDesEmojis[1]:
        await message.channel.send(get_traduction_message("explications envoi roles stonks", donneesAdditionnelles))
        guildsData[str(message.guild.id)]["rolesPingStonks"] = []
        messageToInteractWith[(message.channel.id, donneesAdditionnelles)] = (
        modifier_roles_ping_message, donneesAdditionnelles)


async def modifier_roles_ping_message(message, donneesAdditionnelles):
    global guildsDataModified
    if message.content.lower() == "done":
        messageToInteractWith.pop((message.channel.id, donneesAdditionnelles))
        aEnvoyer = get_traduction_message("affichage roles ping stonks 1", donneesAdditionnelles)
        for i in guildsData[str(message.guild.id)]["rolesPingStonks"]:
            valeur = i[1]
            if i[1] < 2_000:
                valeur = f"{i[1]*100}%"
            else:
                valeur = jolis_chiffres(i[1])
            aEnvoyer += f"{message.guild.get_role(i[0])} " + get_traduction_message("affichage roles ping stonks 2", donneesAdditionnelles, [valeur])
        await message.channel.send(aEnvoyer)
        guildsDataModified = True
        return
    messageSplitted = message.content.split()
    pourcentage = True
    try:
        int(messageSplitted[0])
        if messageSplitted[1][-1] != "%":
            pourcentage = False
            int(messageSplitted[1])
        else:
            pourcentage_valeur = int(messageSplitted[1][:-1])/100
    except:
        await message.channel.send(get_traduction_message("syntaxe changement roles erronnee", donneesAdditionnelles))
        return

    if len(messageSplitted) != 2 or message.guild.get_role(int(messageSplitted[0])) == None:
        await message.channel.send(get_traduction_message("syntaxe changement roles erronnee", donneesAdditionnelles))
    else:
        if pourcentage:
            if pourcentage_valeur < 0.1 or pourcentage_valeur >= 2_000:
                await message.channel.send(get_traduction_message("erreur benefice min role ping stonks", donneesAdditionnelles))
                return
            guildsData[str(message.guild.id)]["rolesPingStonks"].append(
                (int(messageSplitted[0]), pourcentage_valeur))
            await message.channel.send(f"{message.guild.get_role(int(messageSplitted[0]))} " + get_traduction_message(
                "ajout d'un role ping stonks", donneesAdditionnelles, [f"{pourcentage_valeur*100}%"]))
        else:
            if int(messageSplitted[1]) < 200001:
                await message.channel.send(get_traduction_message("erreur benefice min role ping stonks", donneesAdditionnelles))
                return

            guildsData[str(message.guild.id)]["rolesPingStonks"].append((int(messageSplitted[0]), int(messageSplitted[1])))
            await message.channel.send(f"{message.guild.get_role(int(messageSplitted[0]))} " + get_traduction_message("ajout d'un role ping stonks", donneesAdditionnelles, [jolis_chiffres(int(messageSplitted[1]))]))

async def modifier_channel_stonks_message(message, donneesAdditionnelles):
    global guildsDataModified

    if "done" in message.content:
        messageToInteractWith.pop((message.channel.id, donneesAdditionnelles))
        await message.channel.send(":white_check_mark: done !")
        return
    if len(message.channel_mentions) != 1:
        await message.channel.send(get_traduction_message("erreur mention channel stonks", donneesAdditionnelles))
        return
    message_splitted = message.content.split()
    if len(message_splitted) != 2:
        await message.channel.send(get_traduction_message("erreur arguments channel stonks", donneesAdditionnelles))
        return
    try:
        min_profit = int(message_splitted[1])
    except:
        await message.channel.send(get_traduction_message("erreur chiffre channel stonks", donneesAdditionnelles))
        return

    guildsData[str(message.guild.id)]["channelsStonks"].append((message.channel_mentions[0].id, min_profit))
    guildsDataModified = True
    await message.channel.send(get_traduction_message('channel stonks ajout', donneesAdditionnelles, [message.channel_mentions[0].mention, jolis_chiffres(min_profit)]))

async def cmd_donators(args, message):
    contenu = "Thanks a lot to :\n"
    for i in donators:
        contenu += f"\n - {i}"
    await message.channel.send(embed=await generer_embed(message,
                                                         "Donators / Patrons",
                                                         contenu))

async def cmd_up_time(args, message):
    if message.author.id != 399978674578784286:
        await message.channel.send(":x: Currently disabled")
        return
    last_24h_up = None
    i = 0
    while last_24h_up is None and i+1 < len(upHistory):
        if upHistory[i+1] >= time.time() - 86400: #quand le prochain fait partie des dernières 24h
            last_24h_up = i

    if last_24h_up is None:
        last_24h_up = len(upHistory)-1

    await message.channel.send(f"""Since July, 19th, the bot was working fine for **{round(len(upHistory) / ((round(time.time()) - upHistory[0]) / 60) * 100, 1)}% fine time**
For last 24h, it has been working fine for **{round((len(upHistory) - last_24h_up) / 1440 * 100, 1)}% fine time**""") #1 440 minutes in a day

async def cmd_badmins_commands(args, message):
    if message.author.id == 399978674578784286 or message.author.id == 579573266650497035 or message.author.id == 409395283617644544:
        await message.channel.send(content=get_traduction_message("autorisation accordee", message.author.id))
        if args[1] in commandes_admin:
            await commandes_admin[args[1]](args, message)
        elif args[1] == "help":
            await message.channel.send(f"Liste des commandes : {commandes_admin.keys()}")
        else:
            await message.channel.send(content=":x: Commande admin non trouvée")
    else:
        await message.channel.send(content=get_traduction_message("autorisation refusee bot", message.author.id))
        return

async def cmd_badmin_add_donator(args, message):
    if is_nightly:
        await message.channel.send(":x: I'm on nightly mode")
        return
    global donators
    donators.append("".join(args[2:]))
    await dbtools.modify_data_into_db("donators", generer_string_dune_var(donators))
    await message.channel.send(f"Donator named '{''.join(args[2:])}' added")


async def cmd_badmin_load(args, message):
    await alerte_strasky_serv(f"Attention, la commande load a été utilisée par {message.author}")
    global redemarrerAlias, aliasManquants
    donnees = await message.attachments[0].read()
    donnees = json.loads(donnees)
    hypixelAlias = donnees

    aliasManquants = {}
    redemarrerAlias = True
    await message.channel.send(
        content=f"Succès : Les alias ont étés remplacés par ceux du fichier ({len(hypixelAlias)} items)")
    await message.channel.send(content="Les alias reprenderont d'ici 2 min automatiquement")

async def cmd_badmin_alias_restants(args, message):
    await message.channel.send(
        content=f"sur cette session (items détéctés depuis le lancement du bot), il reste à traiter {len(aliasManquants)} items")

async def cmd_badmin_shutdown(args, message):
    await message.channel.send(content="Arrêt programmé")
    await alerte_strasky_serv(f"Arrêt du bot par {message.author}")
    global arreter
    arreter = True
    await client.change_presence(status=discord.Status.do_not_disturb,
                                 activity=discord.Game(
                                     f"{texteDefaultActivity} - Arrêt en cours"))
    await asyncio.sleep(60) #le bot a 1 min pour s'eteindre
    exit()

async def cmd_badmin_log(args, message):
    await message.channel.send(content="Python logs",
                               file=discord.File("logging.log", "logging.txt"))
    os.system("journalctl -u reboot_bot.service -n 10000 > log.txt")
    await message.channel.send(content="Sys logs",
                               file=discord.File("log.txt", "log.txt"))

async def cmd_badmin_dev(args, message):
    if len(args) < 3:
        log(du.return_firstLayerHashDict())
        log(dataEnchants)
    else:
        key = args[-1] + "L"
        key += " ".join(args[2:-1])
        key_hash = await du.get_first_layer_attributes_hash(key)
        await message.channel.send(f"Searching with key {key} with hash {key_hash}")
        if key_hash in dataEnchants[0]:
            await message.channel.send(f"For classic items : {await trouver_mediane(dataEnchants[0][key_hash], 1)}")
        else:
            await message.channel.send("Not found for classic items")
        if key_hash in dataEnchants[1]:
            await message.channel.send(f"For dungeon items which can be drop enchanted : {await trouver_mediane(dataEnchants[1][key_hash], 1)}")
        else:
            await message.channel.send("Not found for dungeon items which can be drop enchanted")
    """log(await client.get_channel(842453728585973774).fetch_message(855137945848512512).embeds)
    log(maintenance)
    log(await message.guild.fetch_emojis())
    log(soldHistory)
    #await add_items_linked_with_event_in_itemsAffectedTemporarely("Winter Island", time.time()+120)
    if len(args) > 2:
        await message.channel.send(
            content=f"> {message.guild.get_role(842686623313690695).mention} {message.guild.get_role(842686927362719755).mention} {message.guild.get_role(842686965010530305).mention} {message.guild.get_role(842686999352705094).mention} {message.guild.get_role(842687033523568649).mention}",
            embed=await generer_embed(None,
                                      f"Summoning Ring's sell",
                                      "This item is sold at **3.5m** which is cheaper than the average (11.74m less expensive) (by `CTSwat`)\nRarity: RARE\nSummoning Ring's sell quantity (last 24h): **384**",
                                      fields=[
                                          ["Attributes : ",
                                           "3T0SSUMMONING_RING estimated at 15.24m\nSell median in the 2.0 last hours",
                                           False],
                                          ["Sell Price : ", "3.5m", True],
                                          ["Potential resell price : ", "15.24m", True],
                                          ["Potential resell profit : ",
                                           "11.62m that is to say 331%", False],
                                          ["Access : ", f"`/ah CTSWat`", False]
                                      ],
                                      thumbnail=args[2]))
    else:
        await message.channel.send(
            content=f"> {message.guild.get_role(842686623313690695).mention} {message.guild.get_role(842686927362719755).mention} {message.guild.get_role(842686965010530305).mention} {message.guild.get_role(842686999352705094).mention} {message.guild.get_role(842687033523568649).mention}",
            embed=await generer_embed(None,
                                      f"Summoning Ring's sell",
                                      "This item is sold at **3.5m** which is cheaper than the average (11.74m less expensive) (by `CTSwat`)\nRarity: RARE\nSummoning Ring's sell quantity (last 24h): **384**",
                                      fields=[
                                          ["Attributes : ",
                                           "3T0SSUMMONING_RING estimated at 15.24m\nSell median in the 2.0 last hours",
                                           False],
                                          ["Sell Price : ", "3.5m", True],
                                          ["Potential resell price : ", "15.24m", True],
                                          ["Potential resell profit : ",
                                           "11.62m that is to say 331%", False],
                                          ["Access : ", f"`/ah CTSWat`", False]
                                      ],
                                      thumbnail="https://images-ext-2.discordapp.net/external/PjjRdeSl2TQQApwL8BS3ufT3-shdf1Fkx1EsKQnizyk/%3Fcb%3D20191018090137/https/static.wikia.nocookie.net/hypixel-skyblock/images/c/cc/Barrier.png/revision/latest"))"""

async def cmd_badmin_valider(args, message):
    await alerte_strasky_serv(f"Attention, la commande valider a été utilisée par {message.author}")
    await message.channel.send(content=f"Sauvegarde des alias ({len(hypixelAlias)} items) en envoi...")
    aEnvoyer = json.dumps(hypixelAlias)
    timestampActu = get_current_utc_timestamp()
    fichier = io.BytesIO(bytes(aEnvoyer, "utf-8"))
    await message.channel.send(
        content=f"Données du {datetime.fromtimestamp(time.time())} (UTC {round(time.timezone * -1 / 3600)})",
        file=discord.File(fichier, f"alias-{datetime.fromtimestamp(timestampActu)}.json"))

async def cmd_badmin_hash_dict(args, message):
    await message.channel.send(":x: Désactivé")
    """await alerte_strasky_serv(f"Attention, la commande valider a été utilisée par {message.author}")
    await message.channel.send(content=f"Dictionnaire des hashs en envoi...")
    du.update_fichier_hashs()
    timestampActu = get_current_utc_timestamp()
    fichier = "data/hash-dict.json"
    await message.channel.send(
        content=f"Données du {datetime.fromtimestamp(time.time())} (UTC {round(time.timezone * -1 / 3600)})",
        file=discord.File(fichier, f"hash-dict-{datetime.fromtimestamp(timestampActu)}.json"))
    #log(soldHistory)"""

async def cmd_badmin_activer_alias_editing(args, message):

    if len(args) < 3:
        await message.channel.send(content=":x: Aucun argument détécté, attendu : start / stop")
        return
    if args[2] == "stop":
        if not loop_alias.is_running():
            await message.channel.send(content=":warning: Le système d'édition des alias est déjà désactivé")
        else:
            loop_alias.cancel()
            await message.channel.send(content="L'opération a été effectuée (sans vérification de succès)")

    elif args[2] == "start":
        if loop_alias.is_running():
            await message.channel.send(content=":warning: Le système d'édition des alias est déjà activé")
        else:
            loop_alias.start()
            await message.channel.send(content="L'opération a été effectuée (sans vérification de succès)")
    else:
        await message.channel.send(content=":x: Argument refusé, attendu : start / stop")

async def cmd_badmin_sleep(args, message):
    if len(args) < 3:
        await message.channel.send(content=":x: Aucun argument détécté, attendu : start / stop")
        return
    if args[2] == "start":
        if not loop_traiter_donnees_api.is_running():
            await message.channel.send(content=":warning: Le système d'actualisation des données est déjà désactivé")
        else:
            loop_traiter_donnees_api.cancel()
            await message.channel.send(content="L'opération a été effectuée (sans vérification de succès)")

    elif args[2] == "stop":
        if loop_traiter_donnees_api.is_running():
            await message.channel.send(content=":warning: Le système d'actualisation des données est déjà activé")
        else:
            loop_traiter_donnees_api.start()
            await message.channel.send(content="L'opération a été effectuée (sans vérification de succès)")
    else:
        await message.channel.send(content=":x: Argument refusé, attendu : start / stop")

async def cmd_badmin_show_vars(args, message):
    global hypixelDataPrices, dataAttributesPrices, dataReforgesPrices, dataPetsPrices, dataDonneesAdditionnellesPrices, numberTimeItemWithAttributesSold
    log(hypixelDataPrices)
    log(dataAttributesPrices)
    log(dataReforgesPrices)
    log(dataPetsPrices)
    log(dataDonneesAdditionnellesPrices)
    log(numberTimeItemWithAttributesSold)
    await message.channel.send(content="Envoyé dans la console !")

async def cmd_badmin_is_stonks(args, message):
    global isStonksEnabled
    if len(args) < 3:
        await message.channel.send(content=":x: Aucun argument détécté, attendu : start / stop")
        return
    if args[2] == "stop":
        if not isStonksEnabled:
            await message.channel.send(content=":warning: Le système is_stonks est déjà désactivé")
        else:
            isStonksEnabled = False
            await message.channel.send(content="L'opération a été effectuée (sans vérification de succès)")

    elif args[2] == "start":
        if isStonksEnabled:
            await message.channel.send(content=":warning: Le système is_stonks est déjà activé")
        else:
            isStonksEnabled = True
            await message.channel.send(content="L'opération a été effectuée (sans vérification de succès)")
    else:
        await message.channel.send(content=":x: Argument refusé, attendu : start / stop")

async def cmd_badmin_alerte_stonks(args, message):
    global stonksAlert
    if len(args) < 3:
        await message.channel.send(content=":x: Aucun argument détécté, attendu : start / stop")
        return
    if args[2] == "stop":
        if not stonksAlert:
            await message.channel.send(content=":warning: Le système d'alerte stonks est déjà désactivé")
        else:
            stonksAlert = False
            await message.channel.send(content="L'opération a été effectuée (sans vérification de succès)")

    elif args[2] == "start":
        if stonksAlert:
            await message.channel.send(content=":warning: Le système d'alerte stonks est déjà activé")
        else:
            stonksAlert = True
            await message.channel.send(content="L'opération a été effectuée (sans vérification de succès)")
    else:
        await message.channel.send(content=":x: Argument refusé, attendu : start / stop")


async def cmd_badmin_temp_affected_items(args, message):
    global itemsAffectedTemporarely
    if len(args) < 4 or len(args) > 5:
        await message.channel.send(":x: Nombre d'arguments inccorects, ah$badmin temp-affected ID écart_timestamp duree_de_validite")
        return
    elif args[2] not in hypixelAlias:
        await message.channel.send(":x: L'id d'item n'est pas dans la base de données Alias")
        return
    elif args[3] != "None":
        try:
            args[3] = int(args[3])
        except:
            await message.channel.send("L'écart de timestamp est incorrect (ni None ni nombre)")
            return
    else:
        args[3] = None

    if args[2] in itemsAffectedTemporarely:
        await message.channel.send(f"L'item était déjà affecté, anciennes données écrasées : {itemsAffectedTemporarely[args[2]]}")
    if len(args) != 5:
        args.append(None)
    elif args[4] != "None":
        try:
            args[4] = int(args[4])
        except:
            await message.channel.send("Le timestamp de péremption est incorrect (ni None ni nombre)")
            return
    else:
        args[4] = None

    itemsAffectedTemporarely[args[2]] = [args[3], args[4]]
    await message.channel.send(f"L'item id={args[2]} a pour écart max avec l'heure actuelle de {args[3]} secondes, cela est valable jusqu'à {args[4]}")
    await alerte_strasky_serv(
        f"L'item id={args[2]} a pour écart max avec l'heure actuelle de {args[3]} secondes, cela est valable jusqu'à {args[4]} (par {message.author.name})")

async def cmd_badmin_event(args, message):
    if args < 2:
        await message.channel.send(":x: Arguments nécessaires : event")
    else:
        if args[1] in items_linked_events:
            try:
                await add_items_linked_with_event_in_itemsAffectedTemporarely(args[1])
            except:
                await message.channel.send(":x: Erreur")
        else:
            await message.channel.send(":x: Event inconnu")

async def cmd_badmin_status(args, message):
    if len(args) < 2:
        await message.channel.send(":x: Argument nécessaire : status")
    elif args[2] != "online" and args[2] != "offline" and args[2] != "maintenance":
        await message.channel.send(":x: Argument incorrect doit être online/offline/maintenance")
    else:
        await modify_state(args[2])
        await message.channel.send("Effectué sans vérification de succès")

async def cmd_badmin_ram(args, message):
    global show_ram
    show_ram = True
    await message.channel.send("la RAM sera affichée dans la console")

async def cmd_badmin_disable(args, message):
    global itemsAffectedTemporarely
    if len(args) != 3:
        await message.channel.send(":x: You must have 1 argument, the item_id")
        return
    if args[2] not in hypixelAlias:
        await message.channel.send(":x: Item id not in the data base")
        return
    itemsAffectedTemporarely[args[2]] = [None, round(time.time())+14400]
    await message.channel.send(f"item {hypixelAlias[args[2]]} disable for 4 hours")

async def cmd_badmin_reboot(args, message):
    await message.channel.send("The bot will shutdown, and automatically reboot")
    exit()

async def cmd_badmin_sql(args, message):
    await message.channel.send(f"Sending command {' '.join(args[2:])}")
    await message.channel.send(f"Result : {await dbtools.cmd(' '.join(args[2:]))}")

commandes = {
    "ping": cmd_ping,
    "online-time": cmd_online_time,
    "price": cmd_price,
    "search": cmd_search,
    "config": cmd_config_generic,
    "help": cmd_help,
    "stats": cmd_stats,
    "next-events": cmd_next_events,
    "current-events": cmd_current_events,
    "events": cmd_events,
    "donators": cmd_donators,
    "donator": cmd_donators,
    "badmin": cmd_badmins_commands,
    "uptime": cmd_up_time
}
commandes_admin = {
    "alias-editing": cmd_badmin_activer_alias_editing,
    "sleep": cmd_badmin_sleep,
    "show-vars": cmd_badmin_show_vars,
    "is_stonks": cmd_badmin_is_stonks,
    "alerte-stonks": cmd_badmin_alerte_stonks,
    "temp-affected": cmd_badmin_temp_affected_items,
    "valider": cmd_badmin_valider,
    "load": cmd_badmin_load,
    "alias-restants": cmd_badmin_alias_restants,
    "shutdown": cmd_badmin_shutdown,
    "dev": cmd_badmin_dev,
    "event": cmd_badmin_event,
    "status": cmd_badmin_status,
    "ram": cmd_badmin_ram,
    "hash-dict": cmd_badmin_hash_dict,
    "log": cmd_badmin_log,
    "disable": cmd_badmin_disable,
    "reboot": cmd_badmin_reboot,
    "sql": cmd_badmin_sql
}
commandesAlias = {
    "alias-restant": "alias-restants",
    "srch": "search"
}


client = discord.Client()

reactionToInteractWith = {} #dico sous la forme (id_message, id_author): (commande, dataAdditionnelle (sous n'importe quelle forme))
messageToInteractWith = {} #dico sous la forme (id_channel, id_author): (commande, dataAdditionnelle (sous n'importe quelle forme))

@client.event
async def on_ready():
    global is_nightly
    if len(client.guilds) > 2:
        log("Le bot est sur + de 2 serveurs !!")
        await alerte_strasky_serv("Le bot est sur + de 2 serveurs !!")

    await client.change_presence(status=discord.Status.online, activity=defaultActivity)
    log(f'{client.user} has connected to Discord!')
    if not maintenance:
        await modify_state("online")


@client.event
async def on_message(message):
    global bot_stats
    if message.channel.id == 845351604001439765:
        await add_leaks(message)
    elif message.channel.id == 842482146928099350:
        await add_news(message)
    if not message.author.bot:
        # les réponses aux messages randoms
        """if "t'es pas bo" in message.content or "t'es pas beau" in message.content:
            await message.channel.send(content="snifff je suis vexé, je ne te parle plus")
        elif "patate" in message.content.lower():
            await message.channel.send(content="PATATE :potato:")
        elif "potato" in message.content.lower():
            await message.channel.send(content="POTATO :potato:")"""
        global hypixelAlias, messageToInteractWith
        if (message.channel.id, message.author.id) in messageToInteractWith:
            await messageToInteractWith[(message.channel.id, message.author.id)][0](message, messageToInteractWith[(message.channel.id, message.author.id)][1])
            #messageToInteractWith.pop((message.channel.id, message.author.id))
        # les commandes
        if message.content[0:len(prefix)] == prefix and (not is_nightly or message.channel.id == 856251437041188864):
            try:
                bot_stats["commandes"] += 1
            except:
                bot_stats["commandes"] = 1
                await alerte_strasky_serv("on_message : bot_stats commandes erreur, handled")

            messageSansPrefix = message.content[len(prefix):]

            args = messageSansPrefix.split()
            args[0] = args[0].lower()

            if args[0] in commandes:
                await commandes[args[0]](args, message)
            elif args[0] in commandesAlias:
                await commandes[commandesAlias[args[0]]](args, message)
            else:
                await message.channel.send(content=get_traduction_message("commande inconnue", message.author.id))


@client.event
async def on_reaction_add(reaction, user):
    global reactionToInteractWith
    user = None
    estDansReactionToInteract = False
    async for user in reaction.users(limit=20):
        if (reaction.message.id, user.id) in reactionToInteractWith and user.bot == False:
            estDansReactionToInteract = True
            break
    if estDansReactionToInteract:
        await reactionToInteractWith[(reaction.message.id, user.id)][0](reaction.message, reaction, reactionToInteractWith[(reaction.message.id, user.id)][1], user.id)
        reactionToInteractWith.pop((reaction.message.id, user.id))

#--- Fonctions Réactions---
async def price_reaction(message, reaction, donneesAdditionnelles, user_id):
    #log(reaction.emoji)
    await cmd_price_step2(donneesAdditionnelles["recherche_possible"][indexDUnEmoji[reaction.emoji]-1], message, user_id, donneesAdditionnelles["duration"]) #on lance l'étape 2 avec l'id de l'item choisi en paramètre

async def add_items_linked_with_event_in_itemsAffectedTemporarely(event_name, timestamp_expiring):
    global itemsAffectedTemporarely
    if event_name not in items_linked_events:
        await alerte_strasky_serv(f"event : {event_name} not found in items_linked_events")
        return
    pas_deja_dans_var = False
    items_linked_with_this_event = []
    for item_id in items_linked_events[event_name]:
        if item_id not in itemsAffectedTemporarely:
            itemsAffectedTemporarely[item_id] = [600, timestamp_expiring] #les medianes doivent etre sur 10 min
            log(f"added event {event_name} : {item_id}")
            items_linked_with_this_event.append(item_id)
            pas_deja_dans_var = True
    if pas_deja_dans_var:
        await alerte_strasky_serv(f"ajout des items liés à l'event {event_name} : {items_linked_with_this_event}")
        events_a_envoyer = current_events(events_timings_data)
        dejaTrouve = False
        if event_name == "New Year Celebration":
            events_a_envoyer = []
        for i in range(len(events_a_envoyer)):
            if not dejaTrouve and events_a_envoyer[i][0] == event_name:
                events_a_envoyer = events_a_envoyer[i]
                dejaTrouve = True
        if len(events_a_envoyer) < 1:
            await alerte_strasky_serv("add_items_linked_with_event_in_itemsAffectedTemporarely: Aucun event en cours détécté")
            return
        if not maintenance:
            async for message in client.get_guild(842453728154091561).get_channel(853182979005087764).history(limit=1):
                if event_name not in message.content:
                    message_alerte = await client.get_channel(853182979005087764).send(
                        f"<@&849292716788940841> **Event {event_name} is coming soon (less than {joli_heure(events_a_envoyer[2])})**\nIt will end in **{joli_heure(events_a_envoyer[1] - time.time())}** (until {datetime.fromtimestamp(events_a_envoyer[1])} UTC+0)")
                    await message_alerte.publish()
        """else:
            await alerte_strasky_serv(
                f"<@&849292716788940841> **Event {event_name} is coming soon (less than {joli_heure(events_a_envoyer[2])})**\nIt will end in **{joli_heure(events_a_envoyer[1] - time.time())}** (until {datetime.fromtimestamp(events_a_envoyer[1])} UTC+0)")
        """
async def search_algorithm(recherche, baseDeDonneesRecherche: dict, nbARetourner=None):
    #la base de donnee doit être sous la forme base={resultat: (motRecherche, x)} (tuple ou list)
    motsRecherche = recherche.lower().split()
    resultatsRecherche = [] #sous la forme (id, points) et RANGE DANS L'ORDRE DECROISSANT
    if nbARetourner == None:
        nbARetourner = len(baseDeDonneesRecherche)

    for donnee in tuple(baseDeDonneesRecherche.items()): #on met en tuple pour si base données modifiées en cours
        pointsTotauxActu = 0 #10 points répartis sur tous les mots-clés de recherche
        donneeLowerSplitted = donnee[1][0].lower().split()

        for motActu in motsRecherche: #pour tester avec tous les mots
            meilleursPoints = 0 #meilleur nombre de points possibles avec ce mot-clé
            for indexDonneeActu in range(len(donneeLowerSplitted)):
                if motActu in donneeLowerSplitted[indexDonneeActu]:
                    pointsCalcules =  len(motActu) / len(recherche) * 10 #la portion des mots-clés représentée par ce mot
                    pointsCalcules /= abs(len(donneeLowerSplitted[indexDonneeActu]) - len(motActu)) + 1 #on divise par la différence de taille des mots (+1 pour éviter division par zéro)
                    if pointsCalcules > meilleursPoints:
                        meilleursPoints = pointsCalcules

            pointsTotauxActu += meilleursPoints

        pointsTotauxActu = round(pointsTotauxActu, 3) #on conserve uniquement 3 décimales
        if len(resultatsRecherche) < nbARetourner or pointsTotauxActu > resultatsRecherche[-1][1]:
            # si on a pas encore rempli resultatsRecherche ou si la donnnée actuelle fait un meilleur score que la meilleure de resultatsRecherche
            indexResultatsANePasDepasser = len(resultatsRecherche) - 1
            if len(resultatsRecherche) < nbARetourner: #si on a pas encore rempli resultatsRecherche
                indexResultatsANePasDepasser = len(resultatsRecherche) #pour pouvoir ajouter un élément
            i = 0
            while i < indexResultatsANePasDepasser and pointsTotauxActu < resultatsRecherche[i][1]:
                i += 1
            resultatsRecherche.insert(i, (donnee[0], pointsTotauxActu)) #on insère dans l'ordre décroissant
            if len(resultatsRecherche) > nbARetourner: #si on dépasse le nombre de résultats maxi
                resultatsRecherche.pop() #on enleve le dernier element
    return resultatsRecherche


async def modify_state(state: str):
    if is_nightly:
        return
    global discordStatus, maintenance
    guild = client.get_guild(842453728154091561)
    emojis = [
        await guild.fetch_emoji(849579230438096928),
        await guild.fetch_emoji(849579168831373312),
        await guild.fetch_emoji(849579205196775434)
    ]
    messages = {
        "online": [f"{emojis[0]} Bot online", discord.Status.online, False],
        "offline": [f"{emojis[1]} Bot offline", discord.Status.online, False],
        "maintenance": [f"{emojis[2]} Bot in maintenance", discord.Status.idle, True]
    }
    if state not in messages:
        await alerte_strasky_serv("modify_state : Erreur state not in list")
        return
    message_state = await client.get_guild(842453728154091561).get_channel(849178577551097876).fetch_message(
        849589897077850212)
    await message_state.edit(content=f"{messages[state][0]}")
    discordStatus = messages[state][1]
    maintenance = messages[state][2]
    await dbtools.modify_data_into_db("maintenance", json.dumps(maintenance))

def generer_string_dune_var(var):
    return str(base64.b64encode(gzip.compress(bytes(json.dumps(var), "utf-8"))))[2:-1]

def generer_var_dun_string(var_string):
    return json.loads(gzip.decompress(base64.b64decode(var_string)))

def get_next_events(events_timings):
    start_timestamp = events_timings["start_timestamp"]
    while start_timestamp + events_timings["1_year"] < time.time():
        start_timestamp += events_timings["1_year"]
    aReturn = {}
    for event_actu in events_list:
        timestamp_event = start_timestamp + events_timings[event_actu]['start']
        while timestamp_event < time.time():
            timestamp_event += events_timings["1_year"]
        aReturn[event_actu] = timestamp_event
    return aReturn

def refresh_events():
    global next_events
    timestamp_min = None
    for event_actu in next_events.values():
        if timestamp_min is None or event_actu < timestamp_min:
            timestamp_min = event_actu
    if timestamp_min is None or timestamp_min < time.time():
        next_events = get_next_events(events_timings_data)
    return next_events

def current_events(events_timings, ecart_selon_event=True):
    start_timestamp = events_timings["start_timestamp"]
    while start_timestamp + events_timings["1_year"] < time.time():
        start_timestamp += events_timings["1_year"]
    current_events_list = []

    for event_actu in events_list:
        if ecart_selon_event:
            ecart = events_timings_data[event_actu]["ecart"]
        else:
            ecart = 0
        if start_timestamp + events_timings_data[event_actu]["start"] <= time.time() + ecart and\
            start_timestamp + events_timings_data[event_actu]["start"] + events_timings_data[event_actu]["duration"] + ecart >= time.time():
            current_events_list.append([event_actu, start_timestamp + events_timings_data[event_actu]["start"] + events_timings_data[event_actu]["duration"] + ecart, start_timestamp + events_timings_data[event_actu]["start"] - time.time()])
    return current_events_list


def get_traduction_message(message_name: str, author_id, vars_a_inclure=[]):
    if type(author_id) == int:
        author_id = str(author_id)
    langActu = "en"
    try:
        langActu = playersData[author_id]["lang"]
    except:
        if author_id not in playersData:
            playersData[author_id] = {}
        playersData[author_id]["lang"] = "en"

    message = ""
    for i in range(len(traductions[message_name][langActu])):
        message += str(traductions[message_name][langActu][i])
        if i < len(vars_a_inclure):
            message += str(vars_a_inclure[i])
    return message

async def add_leaks_or_news(message, var, var_name):
    a_supprimer = [" @SkyBlock Leaks", " @everyone"]
    contenu_message = message.content
    index_a_supprimer = None
    for chaine in a_supprimer:
        if contenu_message.find(chaine) != -1:
            index_a_supprimer = [contenu_message.find(chaine), contenu_message.find(chaine) + len(chaine)]
    if index_a_supprimer != None:
        contenu_message = contenu_message[:index_a_supprimer[0]] + contenu_message[index_a_supprimer[1]:]
    
    r = ""
    for i in contenu_message:
        if i != "'" and i != '"':
            r += i
        else:
            r += " "
    contenu_message = r

    attachment = None
    for i in message.attachments:
        try:
            if "image" in i.content_type.split():
                attachment = i.url
            else:
                log("Leaks or news error : content_type d'un attachments != image")
        except:
            log("Leaks or news error : content_type d'un attachments != image")
    for i in message.embeds:
        if i.type == "image":
            attachment = i.url

    var.append([contenu_message, round(message.created_at.timestamp()), attachment])
    if not is_nightly:
        await dbtools.modify_data_into_db(var_name, json.dumps(var))

async def add_leaks(message):
    global leaks
    log("ajout d'un leaks")
    await add_leaks_or_news(message, leaks, "leaks")

async def add_news(message):
    global news
    log(news)
    log("ajout d'une news")
    await add_leaks_or_news(message, news, "news")



async def generer_embed(message: any, titre, contenu, *, fields=[], footer="🛠️ Made by LupyXev#5816, Strasky#6559 and Saderfing#5924", color=0x1c86ff, thumbnail=None, link=lienDInvitation):
    embed = discord.Embed(title=titre,
        description=contenu,
        color=color,
        url=link
    )
    if message != None:
        embed.set_author(name="To " + message.author.display_name, icon_url=message.author.avatar_url)
    if thumbnail != None:
        embed.set_thumbnail(url=thumbnail)

    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=field[2])

    embed.set_footer(text=footer)

    return embed

async def get_item_image_link(item, rarity=None):
    if item == None: #si on a pas d'item
        return "https://static.wikia.nocookie.net/hypixel-skyblock/images/c/cc/Barrier.png/revision/latest?cb=20191018090137"

    session = aiohttp.ClientSession()
    link = "https://skyblock-api.dedria.com/api/items?search=" + item
    if rarity != None:
        link += "&meta_rarity=" + rarity
    async with session.get(link,
                           headers={"accept": "application/json",
                                    "authorization": f"Bearer {TOKEN_ITEMS_API}"}) as resp:
        respJSON = await resp.json()
    await session.close()
    try:
        return respJSON["data"][0]["image"]
    except:
        return "https://static.wikia.nocookie.net/hypixel-skyblock/images/c/cc/Barrier.png/revision/latest?cb=20191018090137"

def get_auction_number():
    reponseJSON = get_auctions()
    return reponseJSON["totalAuctions"], reponseJSON["lastUpdated"]


def get_auctions():
    resp = requests.get(url=url + "auctions", params={"key": TOKEN_HYPIXEL})
    return resp.json()


def get_data_prices():
    with open("data.json", "r") as fichier:
        data = fichier.read()

    return json.loads(data)


def get_price_object(dataPrices, nomItem):
    nomItem = nomItem.lower()
    nomItem = nomItem.replace(" ", "_")
    for i in dataPrices:
        if i["name"] == nomItem:
            return i["low"]


def jolis_chiffres(chiffre, precision=2):
    arrondis = [round(chiffre, 1), round(chiffre / 1_000, precision), round(chiffre / 1_000_000, precision)]
    if arrondis[0] >= 1_000:  # >999
        if arrondis[1] >= 1_000:  # > 999 999
            if arrondis[2] >= 1_000:# > 999 999 999
                return str(round(chiffre / 1_000_000_000, precision)) + "B"
            else:
                return str(arrondis[2]) + "M"
        else:
            return str(arrondis[1]) + "k"
    else:
        return str(arrondis[0])

def joli_heure(timestamp):
    a = datetime.fromtimestamp(round(timestamp))
    if round(timestamp) >= 86400:
        return f"{a.day-1}d {a.hour}h {a.minute}m {a.second}s"
    elif round(timestamp) >= 3600:
        return f"{a.hour}h {a.minute}m {a.second}s"
    elif round(timestamp) >= 60:
        return f"{a.minute}m {a.second}s"
    return f"{a.second}s"

def joli_heure_to_timestamp(joli_heure):
    lettres_avec_valeur_en_sec = {"s": 1, "m": 60, "h": 3600, "d": 86400, "j": 86400, "w": 604800}
    '''mot_avec_valeur_en_sec = {"second": 1, "seconde": 1, "minute": 60, "minut": 60, "hour": 3600, "heure": 3600,
                              "jour": 86400, "day": 86400,
                              "seconds": 1, "secondes": 1, "minutes": 60, "minuts": 60, "hours": 3600, "heures": 3600,
                              "jours": 86400, "days": 86400
                              }'''
    nombres_valides = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", ","]

    tab_avec_int_et_lettre_ou_mot = []  # sous la forme [[lettre, valeur], ..]

    chaine_actu = ["", ""]  # [chaine_mots, chaine_valeur]
    for i in range(len(joli_heure)):
        # on considère que l'utilisateur rentre toujours le nombre puis la lettre/mot

        if joli_heure[i] in nombres_valides:
            if chaine_actu[0] != "":
                try:
                    tab_avec_int_et_lettre_ou_mot.append([chaine_actu[0], float(chaine_actu[1])])
                except:
                    pass
                    #log("erreur impossible de mettre en int ?")
                chaine_actu = ["", ""]
            chaine_actu[1] += joli_heure[i]
        elif joli_heure[i] in lettres_avec_valeur_en_sec.keys():
            chaine_actu[0] += joli_heure[i]
        else:
            if chaine_actu[0] != "" and chaine_actu[1] != "":
                try:
                    tab_avec_int_et_lettre_ou_mot.append([chaine_actu[0], float(chaine_actu[1])])
                except:
                    #log("erreur impossible de mettre en int ?")
                    pass
                chaine_actu = ["", ""]

    if chaine_actu[0] != "" and chaine_actu[1] != "":
        try:
            tab_avec_int_et_lettre_ou_mot.append([chaine_actu[0], float(chaine_actu[1])])
        except:
            pass
            #log("erreur impossible de mettre en int ?")

    total = 0
    # on additionne tout
    for val in tab_avec_int_et_lettre_ou_mot:
        if val[0] in lettres_avec_valeur_en_sec:
            total += val[1] * lettres_avec_valeur_en_sec[val[0]]
        else:
            log("Erreur lors de l'addition")
    #log(total)
    return total


def get_premier_bin():
    reponseJSON = get_auctions()
    i = 0

    listeBin = []
    dataPrices = get_data_prices()

    for i in range(1000):

        if "bin" in list(reponseJSON["auctions"][i].keys()):

            prixObjet = get_price_object(dataPrices, reponseJSON["auctions"][i]["item_name"])

            if prixObjet != None and reponseJSON["auctions"][i]["starting_bid"] < prixObjet * 0.6:
                listeBin.append({
                    "numeroListe": i,
                    "nomItem": reponseJSON["auctions"][i]["item_name"],
                    "prixItem": jolis_chiffres(reponseJSON["auctions"][i]["starting_bid"]),
                    "pourcentageParRapportAuPrixHabituel": round(
                        reponseJSON["auctions"][i]["starting_bid"] / prixObjet * 100)
                })

    return listeBin


async def alerte_strasky_serv(messageAlerte):
    await client.get_channel(813801717572960316).send(
        f"{datetime.fromtimestamp(time.time())} (UTC {round(time.timezone * -1 / 3600)}) : {messageAlerte}")

def get_current_utc_timestamp():
    return time.time()


async def get_nbPages_et_lastHypixelApiUpdate():
    session = aiohttp.ClientSession()
    async with session.get(url + "auctions", params={"key": TOKEN_HYPIXEL}) as resp:
        reponseJSON = await resp.json()
    await session.close()
    return int(reponseJSON["totalPages"]), reponseJSON["lastUpdated"]


async def verifier_auctions_encore_existing(duree_max, token_history, auctionsInteressantes_actu, session):
    if auctionsInteressantes_actu is None:
        await asyncio.sleep(duree_max)
        return token_history, auctionsInteressantes_actu
    timestampFin = time.time() + duree_max
    timeout = aiohttp.ClientTimeout(total=3)
    if duree_max < 2:
        return token_history, auctionsInteressantes_actu
    timestampDepart = time.time()
    token_history_cleaned = []
    for i in token_history:
        if i >= time.time() - 60:
            token_history_cleaned.append(i)
    token_history = token_history_cleaned
    i = 0
    tab_auctions_interessantes = tuple(auctionsInteressantes_actu.keys())
    #log(f"\ntabauctions {tab_auctions_interessantes}")
    while time.time() < timestampFin and len(token_history) < 110 and i < len(tab_auctions_interessantes):

        async with session.get(url + "auction", params={"key": TOKEN_HYPIXEL, "uuid": tab_auctions_interessantes[i]}, timeout=timeout) as resp:

            respJSON = await resp.json()
            if respJSON["success"] is not True:
                log(f"Impossible de charger la page de l'auction {tab_auctions_interessantes[i]}")
            else:
                if len(respJSON["auctions"]) < 1 or respJSON["auctions"][0]["end"]/1000 <= time.time():
                    #auction expirée ou annulée
                    #on ne pop pas car cela permet d'avoir les infos de ventes quand l'auction n'est déjà plus affichée sur l'API
                    #messages = auctionsInteressantes_actu.pop(tab_auctions_interessantes[i])
                    messages = auctionsInteressantes_actu[tab_auctions_interessantes[i]]
                    try:
                        if len(respJSON["auctions"][0]["bids"]) > 0:
                            player_name = await get_player_name_by_api(respJSON["auctions"][0]["bids"][0]["bidder"], session)
                            embed = await generer_embed(None, messages[2],
                                                        f"__**SOLD**__ *in {round(respJSON['auctions'][0]['end']/1000 - messages[3])}s*, for {messages[1][0]} estimated profit ({messages[1][1]}%)\nBought by `{player_name}`",
                                                        thumbnail="https://media.discordapp.net/attachments/811611272251703357/850051408782819368/sold-stamp.jpg",
                                                        color=0xe62e00)
                        else:
                            embed = await generer_embed(None, messages[2],
                                                                              f"__**CANCELLED OR EXPIRED**__ *in {round(time.time() - messages[3])}s*",
                                                                              thumbnail="https://cdn.discordapp.com/attachments/811611272251703357/859424405432041492/exired_v2.png",
                                                                              color=0xe62e00)
                    except:
                        embed = await generer_embed(None, messages[2],
                                                    f"__**CANCELLED OR EXPIRED**__ *in {round(time.time() - messages[3])}s* *(it could be also sold)*",
                                                    thumbnail="https://cdn.discordapp.com/attachments/811611272251703357/859424405432041492/exired_v2.png",
                                                    color=0xe62e00)
                    for message_data_actu in messages[0]:
                        try:
                            message_actu = await client.get_channel(message_data_actu[0]).fetch_message(
                                message_data_actu[1])
                            await message_actu.edit(embed=embed)
                        except:
                            log("impossible de modifier une auction annulée")
            token_history.append(time.time())
        i += 1
    if time.time() + 0.1 < timestampFin:
        await asyncio.sleep(timestampFin - time.time())
    return token_history, auctionsInteressantes_actu

async def wait_until_hypixel_api_refresh(nbRun, lastHypixelApiUpdate=None, token_history=None, auctionsInteressantes=None):
    if auctionsInteressantes is None:
        auctionsInteressantes = {}
    global discordStatus
    if tempsDeRafraichissementDeLApi - 60 > 0:
        await client.change_presence(status=discordStatus,
                                     activity=discord.Game(texteDefaultActivity + " - Waiting Hypixel sync"))
        await asyncio.sleep(tempsDeRafraichissementDeLApi - 60)
    await client.change_presence(status=discordStatus, activity=discord.Game(f"{texteDefaultActivity} - Synchronized with Hypixel - Run {nbRun}"))
    hypixelApiUpdated = False
    session = aiohttp.ClientSession()

    # initialisation
    if lastHypixelApiUpdate is None:
        try:
            async with session.get(url + "auctions") as resp:
                reponseJSON = await resp.json()
                lastHypixelApiUpdate = reponseJSON["lastUpdated"]
        except:
            await alerte_strasky_serv("Synchro avec hypixel : Impossible de charger la page")

    while hypixelApiUpdated is False:

        if speedUpdate: log("chargement")

        try:
            async with session.get(url + "auctions") as resp:
                reponseJSON = await resp.json()
                if lastHypixelApiUpdate != int(reponseJSON['lastUpdated']):
                    hypixelApiUpdated = True
                    await session.close()
                    return int(reponseJSON["totalPages"]), reponseJSON["lastUpdated"], token_history, auctionsInteressantes

                elif int(reponseJSON[
                             'lastUpdated']) / 1000 + 62 - get_current_utc_timestamp() > 0:  # au cas où on ne récupère pas les nouvelles données à T+1 minute 
                    await asyncio.sleep(1)
                    token_history, auctionsInteressantes = await verifier_auctions_encore_existing(int(reponseJSON['lastUpdated']) / 1000 + 62 - get_current_utc_timestamp() - 3, token_history, auctionsInteressantes, session)
                    #await asyncio.sleep(int(reponseJSON['lastUpdated']) / 1000 + 62 - get_current_utc_timestamp())
                    await asyncio.sleep(2)

                else:
                    await asyncio.sleep(1)
                    await verifier_auctions_encore_existing(
                        3, token_history,
                        auctionsInteressantes, session)
                    await asyncio.sleep(1)
                    
                if int(reponseJSON[
                           "lastUpdated"]) / 1000 < get_current_utc_timestamp() - 600:  # si la dernière update date de + de 10 min
                    await alerte_strasky_serv("La lastUpdated de l'API est ancienne de plus de 10 min !")
        except:
            await alerte_strasky_serv("Synchro avec hypixel : Impossible de charger la page")

async def get_player_name_by_api(player_id, session):
    try:
        async with session.get(urlApiUuidToPseudo + str(player_id) + "/json") as resp:
            reponseJSON = await resp.json()
            if "pseudo" in reponseJSON:
                return reponseJSON["pseudo"]
    except:
        await alerte_strasky_serv(
            f"Le joueur ayant pour uuid {player_id} n'est pas trouvé via l'API uuid to username")
        return None


async def is_stonks(auction, session, auction_id, run):
    global guildsData, itemsAffectedTemporarely, bot_stats, maintenance, hypixelApiDataViaUUID, alertsByItemId, itemBans



    if auction["item_id"] in blacklisted_items or auction["item_id"] not in hypixelAlias or "MAP:" in auction["item_id"] or auction["item_id"] == "null":
        return False, None, None

    if timestampDemarrage < get_current_utc_timestamp() + 180:  # on attend un peu avant chaque démarrage pour ajouter des stats
        try:
            bot_stats["auctions scanned"] += 1
        except:
            bot_stats["auctions scanned"] = 1
            await alerte_strasky_serv("is_stonks bot_stats['auction scanned'] : erreur, handled")

        try:
            bot_stats["auctions scanned prices amount"] += auction['starting_bid']
        except:
            bot_stats["auctions scanned prices amount"] = auction['starting_bid']
            await alerte_strasky_serv("is_stonks bot_stats['auctions scanned prices amount'] : erreur, handled")

    timestampMin = round(get_current_utc_timestamp()) - 7200

    if auction["item_id"] in itemsAffectedTemporarely:
        if itemsAffectedTemporarely[auction["item_id"]][1] == None or itemsAffectedTemporarely[auction["item_id"]][1] > get_current_utc_timestamp():
            if itemsAffectedTemporarely[auction["item_id"]][0] == None:
                return False, None, None
            else:
                timestampMin = round(get_current_utc_timestamp()) - itemsAffectedTemporarely[auction["item_id"]][0]

    dungeonItemLvl = auction["dungeon_item_level"]
    nomDuJoueur = None
    attributs = await get_attributs_pour_estimation_prix(auction, False)
    prixCalcule, fiabilite, prixTrouves, timestampMini = await algo_trouver_prix_attributs(attributs, True, True, smartLimitDate=True, returnAllPrices=True, returnTimestampMini=True, timestampMin=timestampMin)

    marge = (200000, new_update_percentage_needed(auction["item_id"]), 40) #pourcentage, pourcentage de la valeur des enchants max

    if prixCalcule == None: #on a pas pu calculer son prix potentiel de vente
        return False, None, None
    if auction["item_id"] in couplesItemsEtRarityToIgnore and auction["tier"] in couplesItemsEtRarityToIgnore[auction["item_id"]]:
        return False, None, None

    prixCalcule *= 0.99

    if prixCalcule > auction["starting_bid"] + marge[0] and\
            prixCalcule > auction["starting_bid"] * (1 + marge[1] / 100) and \
        fiabilite > 7:
        nomDuJoueur = await get_player_name_by_api(auction["auctioneer"], session)

        prixTotalEnchantsEtReforge = 0
        attributsAvecPrixTrouves = []
        listeEnchants = []
        for prixTrouveActu in prixTrouves:
            attributActu = None
            enchant = False
            if len(prixTrouveActu[0]) == 1:
                attributActu = attributs[prixTrouveActu[0][0]]
            elif len(prixTrouveActu[0]) == 2:
                attributActu = attributs[prixTrouveActu[0][0]][prixTrouveActu[0][1]]
                if prixTrouveActu[0][0] == 5 or prixTrouveActu[0][0] == 4:  # si enchant ou reforge
                    if prixTrouveActu[1] > 0:  # si prix > à 0 (sinon on ignore)
                        prixTotalEnchantsEtReforge += prixTrouveActu[1]
                    if prixTrouveActu[0][0] == 5: #si enchant
                        enchant = True
                        listeEnchants.append((f"{attributActu[0]} {attributActu[1]}", jolis_chiffres(prixTrouveActu[1]), prixTrouveActu[2]))

            elif len(prixTrouveActu[0]) == 3:
                attributActu = attributs[prixTrouveActu[0][0]][prixTrouveActu[0][1]][prixTrouveActu[0][2]]
            elif len(prixTrouveActu[0]) == 4:
                attributActu = attributs[prixTrouveActu[0][0]][prixTrouveActu[0][1]][prixTrouveActu[0][2]][
                    prixTrouveActu[0][3]]
            elif len(prixTrouveActu[0]) == 5:
                attributActu = attributs[prixTrouveActu[0][0]][prixTrouveActu[0][1]][prixTrouveActu[0][2]][prixTrouveActu[0][3]][
                    prixTrouveActu[0][4]]
            else:
                await alerte_strasky_serv(f"is_stonks : len(prixTrouveActu[0]) > 5 (ou = à 0) : {prixTrouveActu}")
            if not enchant: attributsAvecPrixTrouves.append((attributActu, jolis_chiffres(prixTrouveActu[1]), prixTrouveActu[2], prixTrouveActu[0][0]))


        if prixTotalEnchantsEtReforge / prixCalcule * 100 > marge[2]:
            if is_nightly: log(f"item ignoré, ses enchants étants une trop grande partie du prix total : {prixTrouves}")
            return False, None, None
        risque = False
        if prixTotalEnchantsEtReforge / prixCalcule * 100 > marge[2] and \
                prixCalcule - auction["starting_bid"] > prixTotalEnchantsEtReforge * 0.5 + (
                prixCalcule - prixTotalEnchantsEtReforge):
            risque = True

        messageAttributs = ""  # le message avec les prix estimés des différents attributs
        for attributActu in attributsAvecPrixTrouves:
            if len(attributActu[0]) == len(auction["item_id"]) + 4 and attributActu[0][4:] == auction["item_id"]:
                messageAttributs += f"this item, {auction['tier']}, is estimated at {attributActu[1]} coins on {attributActu[2]} sales"
            else:
                messageAttributs += f"\n**{index_de_stockage_to_type[attributActu[3]]}** : {attributActu[0]} estimated at {attributActu[1]} *on {attributActu[2]} sales*\n"
        if len(listeEnchants) > 0:
            messageAttributs += f"\n**Enchantments** : {listeEnchants[0][0]} ({listeEnchants[0][1]})"
            for i in range(1, len(listeEnchants)):
                messageAttributs += f" + {listeEnchants[i][0]} ({listeEnchants[i][1]})"
            messageAttributs += " (specified for dungeon item which can be drop enchanted)"
            messageAttributs += "\n"
        messageAttributs += f"\nSold medians in the {round((get_current_utc_timestamp() - timestampMini) / 3600, 1)} last hours"
        messageAttributs += "\n\n─────────────────"

        messageContenu = f'''This item is sold at **{jolis_chiffres(auction['starting_bid'])}** which is cheaper than the average ({jolis_chiffres(prixCalcule / 0.99 - auction['starting_bid'])} less expensive) (by `{nomDuJoueur}`)
        rarity : {auction["tier"]}\n{auction['item_name']}'s sell quantity (last 24h) : **'''
        if attributs[0] in numberTimeItemWithAttributesSold:
            messageContenu += str(len(numberTimeItemWithAttributesSold[attributs[0]]))
        else:
            messageContenu += "0"
        messageContenu += "**"

        if risque:
            messageContenu += "\n ⚠️ This flip seems hazardous, make sure to be able to sell it later"
        try:
            nomItemFromAlias = hypixelAlias[auction['item_id']][0]
        except:
            await alerte_strasky_serv(f"is_stonks : Erreur avec l'alias de {auction['item_id']}")
            nomItemFromAlias = None

        thumbnail = await get_item_image_link(nomItemFromAlias, auction['tier'])

        lowests = [0, 0, 0, 0]
        i = 0
        for value in hypixelApiDataViaUUID.values():
            i += 1
            if value["item_id"] == auction["item_id"] and value["tier"] == auction["tier"] and value["dungeon_item_level"] == auction["dungeon_item_level"]:
                if value["starting_bid"] < lowests[0] or lowests[0] == 0:
                    lowests[0] = value["starting_bid"]
                elif value["starting_bid"] < lowests[1] or lowests[1] == 0:
                    lowests[1] = value["starting_bid"]
                elif value["starting_bid"] < lowests[2] or lowests[2] == 0:
                    lowests[2] = value["starting_bid"]
                elif value["starting_bid"] < lowests[3] or lowests[3] == 0:
                    lowests[3] = value["starting_bid"]

        if run == 1:
            message_lowests = "||Nothing..."
        else:
            message_lowests = "Nothing..."

        if lowests[0] != 0:
            if run == 1:
                message_lowests = f"||{jolis_chiffres(lowests[0])}"
            else:
                message_lowests = f"{jolis_chiffres(lowests[0])}"
        if lowests[1] != 0:
            message_lowests += f", {jolis_chiffres(lowests[1])}"
        else:
            message_lowests += ", nothing"
        if lowests[2] != 0:
            message_lowests += f" and {jolis_chiffres(lowests[2])}"
        else:
            message_lowests += " and nothing"

        if run == 1:
            message_lowests += "|| Lowest bins not accurate"

        hash = await du.get_attributes_hash(attributs)
        if hash in soldHistory:
            if hash in oldSoldHistory:
                items_sold_filtered_by_attribute_hash = soldHistory[hash] + oldSoldHistory[hash]
            else:
                items_sold_filtered_by_attribute_hash = soldHistory[hash]
        elif hash in oldSoldHistory:
            items_sold_filtered_by_attribute_hash = oldSoldHistory[hash]
        else:
            items_sold_filtered_by_attribute_hash = []

        if attributs[0] in numberTimeItemWithAttributesSold:
            number_sold = len(numberTimeItemWithAttributesSold[attributs[0]])
        else:
            log(f"item {attributs[0]}")
            number_sold = 0
        if is_nightly: log(f"{auction['item_name']}")
        trust_rate = await du.get_trust_rate(auction["starting_bid"],
                                             lowests[1:],
                                             number_sold,
                                             prixCalcule / 0.99,
                                             [i for i in items_sold_filtered_by_attribute_hash if i[1] > time.time() - 7200],
                                             is_nightly
                                             )
        if int(round(trust_rate, 1)*10) < 1:
            if auction["item_id"] not in alertsByItemId:
                alertsByItemId[auction["item_id"]] = []
            alertsByItemId[auction["item_id"]].append(round(time.time()))
            return False, None, None

        fp_image_percentage = images_percentage[int(round(trust_rate, 1)*10)]

        #on génère messageContenu et messageAttributs quand même
        embed = await generer_embed(None,
                                            f"{auction['item_name']} sell",
                                            "", fields=[
                                            ["Attributes", messageAttributs, False],
                                            ["Buy Price", str(jolis_chiffres(auction['starting_bid'])), True],
                                            ["Lowest Bins", message_lowests, True],
                                            ["ㅤ", "─────────────────", False],
                                            ["Potential resell profit",
                                             str(jolis_chiffres(
                                                 prixCalcule - auction['starting_bid'])) + " (" + str(
                                                 round((prixCalcule / auction['starting_bid'] - 1) * 100)) + "%)\n\n─────────────────",
                                             True],
                                            ["Potential resell price", str(jolis_chiffres(prixCalcule/0.99)), True],
                                            ["Access", f"`/ah {nomDuJoueur}`\n`/viewauction {auction_id}`", False]
                                            ], thumbnail=fp_image_percentage)


    else:
        return False, None, None

    aReturn = [] #sous la forme [[guild_id, channel_id, embed_message], ...]

    if timestampDemarrage < get_current_utc_timestamp() + 180: #on attend un peu avant chaque démarrage pour ajouter des stats
        try:
            bot_stats["profit"] += prixCalcule - auction['starting_bid']
        except:
            bot_stats["profit"] = prixCalcule - auction['starting_bid']
            await alerte_strasky_serv("is_stonks bot_stats['profit'] : erreur, handled")
        try:
            bot_stats["advise price amount"] += auction['starting_bid']
        except:
            bot_stats["advise price amount"] = auction['starting_bid']
            await alerte_strasky_serv("is_stonks bot_stats['advise price amount'] : erreur, handled")

        try:
            bot_stats["advise amount"] += 1
        except:
            bot_stats["advise amount"] = 1
            await alerte_strasky_serv("is_stonks bot_stats['advise amount'] : erreur, handled")

    if auction["item_id"] in itemBans:
        if itemBans[auction["item_id"]][0] + banLevels[itemBans[auction["item_id"]][1]] > time.time():
            alertsByItemId[auction["item_id"]].append(round(time.time()))
            return False, None, None
        elif itemBans[auction["item_id"]][0] + banLevels[itemBans[auction["item_id"]][1]] + 600 < time.time():
            itemBans.pop(auction["item_id"])

    nb_fois = 0
    if auction["item_id"] in alertsByItemId:
        for i in alertsByItemId[auction["item_id"]]:
            if i > time.time() - 600:
                nb_fois += 1
    if nb_fois >= 8:
        if auction["item_id"] in itemBans:
            if itemBans[auction["item_id"]][1] < 4:
                log(f"Ban de l'item {auction['item_id']} pour {joli_heure(banLevels[itemBans[auction['item_id']][1]+1])}")
                await client.get_channel(860890262612082708).send(f"{datetime.fromtimestamp(time.time())} : Ban de l'item {auction['item_id']} pour {joli_heure(banLevels[itemBans[auction['item_id']][1]+1])}")

                itemBans[auction["item_id"]] = [time.time(), itemBans[auction['item_id']][1] + 1]
                #itemsAffectedTemporarely[auction["item_id"]] = [None, time.time() + banLevels[itemBans[auction["item_id"]][1]]]
            else:
                log(f"Ban de l'item {auction['item_id']} renouvelée pour 24h")
                await client.get_channel(860890262612082708).send(f"{datetime.fromtimestamp(time.time())} : Ban de l'item {auction['item_id']} renouvelée pour 24h")

                itemBans[auction["item_id"]] = [time.time(), 4]
                #itemsAffectedTemporarely[auction["item_id"]] = [None, time.time() + banLevels[itemBans[auction["item_id"]][1]]]
        else:
            await client.get_channel(860890262612082708).send(f"Premier ban de l'item {auction['item_id']} pour {joli_heure(banLevels[1])}")
            log(f"Premier ban de l'item {auction['item_id']} pour {joli_heure(banLevels[1])}")
            itemBans[auction["item_id"]] = [time.time(), 1]
            #itemsAffectedTemporarely[auction["item_id"]] = [None, time.time() + banLevels[1]]
        alertsByItemId[auction["item_id"]].append(round(time.time()))
        return False, None, None

    if not maintenance:
        for guildData in guildsData.items():
            guildObject = client.get_guild(int(guildData[0]))
            if "channelsStonks" not in guildData[1]\
                or "rolesPingStonks" not in guildData[1]\
                or len(guildData[1]["rolesPingStonks"]) < 1\
                or guildObject == None: #si les données ne sont pas utilisables
                pass
            else:
                #channelStonks = guildObject.get_channel(guildData[1]["channelStonks"])
                valeur_channel_la_plus_haute = [None, 0] #channel, valeur
                for channel_data in guildData[1]["channelsStonks"]:
                    if prixCalcule - auction["starting_bid"] >= channel_data[1] and channel_data[1] > valeur_channel_la_plus_haute[1]:
                        valeur_channel_la_plus_haute = channel_data
                if valeur_channel_la_plus_haute[0] != None:
                    role_plus_haut = [None, 0, 0] #role, valeur_de_ping, index_dans_liste_roles
                    pourcentage_plus_haut = [None, 0, 0]
                    roleDataActu_i = -1
                    for roleDataActu_i in range(len(guildData[1]["rolesPingStonks"])):
                        roleDataActu = guildData[1]["rolesPingStonks"][roleDataActu_i]
                        roleActu = guildObject.get_role(roleDataActu[0])

                        if roleDataActu[1] >= 2_000:#valeur absolue
                            if roleActu != None and roleDataActu[1] <= prixCalcule - auction["starting_bid"]:
                                if roleDataActu[1] > role_plus_haut[1]:
                                    role_plus_haut = [roleActu.mention, roleDataActu[1], roleDataActu_i]
                        else:#%
                            if roleActu != None and roleDataActu[1] <= prixCalcule / auction['starting_bid'] - 1:
                                if roleDataActu[1] > pourcentage_plus_haut[1]:
                                    pourcentage_plus_haut = [roleActu.mention, roleDataActu[1], roleDataActu_i]

                    ping = ">"
                    if role_plus_haut[0] is not None:
                        ping += f" {role_plus_haut[0]}"
                    if pourcentage_plus_haut[0] is not None:
                        ping += f" {pourcentage_plus_haut[0]}"
                    color = 0x1a75ff
                    if role_plus_haut[2] < len(nuances):
                        color = nuances[role_plus_haut[2]]

                    if ping != ">":
                        embedActu = embed
                        embedActu.color = color
                        aReturn.append([ping, valeur_channel_la_plus_haute[0], embedActu])
                        #on ajoute le channel pour toutes les alertes
                        aReturn.append([ping, 857696959791235092, embedActu])
    else:
        guildObject = client.get_guild(842453728154091561)
        role_plus_haut = [None, 0, 0]  # role, valeur_de_ping, index_dans_liste_roles
        pourcentage_plus_haut = [None, 0, 0]
        roleDataActu_i = -1
        for roleDataActu_i in range(len(guildsData["842453728154091561"]["rolesPingStonks"])):
            roleDataActu = guildsData["842453728154091561"]["rolesPingStonks"][roleDataActu_i]
            roleActu = guildObject.get_role(roleDataActu[0])

            if roleDataActu[1] >= 2_000:  # valeur absolue
                if roleActu != None and roleDataActu[1] <= prixCalcule - auction["starting_bid"]:
                    if roleDataActu[1] > role_plus_haut[1]:
                        role_plus_haut = [roleActu.mention, roleDataActu[1], roleDataActu_i]
            else:  # %
                if roleActu != None and roleDataActu[1] <= prixCalcule / auction['starting_bid'] - 1:
                    if roleDataActu[1] > pourcentage_plus_haut[1]:
                        pourcentage_plus_haut = [roleActu.mention, roleDataActu[1], roleDataActu_i]
        ping = ">"
        if role_plus_haut[0] is not None:
            ping += f" {role_plus_haut[0]}"
        if pourcentage_plus_haut[0] is not None:
            ping += f" {pourcentage_plus_haut[0]}"
        color = 0x1a75ff
        if role_plus_haut[2] < len(nuances):
            color = nuances[role_plus_haut[2]]

        if ping != ">":
            embedActu = embed
            embedActu.color = color
            aReturn.append([ping, 849910024423866398, embedActu])
    if len(aReturn) < 1:
        return False, None, None
    else:
        if auction["item_id"] not in alertsByItemId:
            alertsByItemId[auction["item_id"]] = []
        alertsByItemId[auction["item_id"]].append(round(time.time()))
        return True, aReturn, [str(jolis_chiffres(prixCalcule - auction['starting_bid'])), str(round((prixCalcule / auction['starting_bid'] - 1) * 100))]



async def trouver_mediane(liste, profondeurDansLaListe=0, returnQtteDonnees=False):
    taille = len(liste)
    if taille % 2 != 0:
        if profondeurDansLaListe == 0:
            if returnQtteDonnees:
                return liste[taille // 2], taille
            return liste[taille // 2]
        elif profondeurDansLaListe == 1:
            if returnQtteDonnees:
                return liste[taille // 2][0], taille
            return liste[taille // 2][0]
        else:
            await alerte_strasky_serv("trouver_mediane() : profondeur non gérée")
            return None
    else:
        if profondeurDansLaListe == 0:
            if returnQtteDonnees:
                return (liste[taille // 2 - 1] + liste[taille // 2]) / 2, taille
            return (liste[taille // 2 - 1] + liste[taille // 2]) / 2
        elif profondeurDansLaListe == 1:
            if returnQtteDonnees:
                return (liste[taille // 2 - 1][0] + liste[taille // 2][0]) / 2, taille
            return (liste[taille // 2 - 1][0] + liste[taille // 2][0]) / 2
        else:
            await alerte_strasky_serv("trouver_mediane() : profondeur non gérée")
            return None

async def recuperer_uniquement_donnee_selon_intervalle_de_temps(tableau, timestampMin=0, timestampMax=999999999999999999, *, smartLimitDate=False, returnTimestampMinAndAuctionNumber=False, itemId=None, itemWithData=None):
    #on considère que le tableau est sous la forme [(donnée, timestamp), ...]
    if type(tableau) != tuple and type(tableau) != list:
        await alerte_strasky_serv("recuperer_uniquement_donnee_selon_intervalle_de_temps: tableau ni tuple ni list")
        log("recuperer_uniquement_donnee_selon_intervalle_de_temps: tableau ni tuple ni list")
        return []
    continuer = True
    aReturn = []
    tempsActu = get_current_utc_timestamp()
    timestampMinActu = get_current_utc_timestamp() - 1800
    quantity = 0
    if smartLimitDate and itemId in itemsAffectedTemporarely:
        if itemsAffectedTemporarely[itemId][0] == None:
            if returnTimestampMinAndAuctionNumber:
                return [], timestampMin, 0
            return []
        elif timestampMin < tempsActu - itemsAffectedTemporarely[itemId][0]:
            timestampMin = tempsActu - itemsAffectedTemporarely[itemId][0]
            if timestampMinActu > timestampMin:
                timestampMinActu = timestampMin
    if not smartLimitDate: timestampMinActu = timestampMin
    while continuer:
        aReturn = []
        for data in tableau:
            if int(data[1]) >= timestampMinActu and int(data[1]) <= timestampMax:
                aReturn.append(data)
        quantity = len(aReturn)
        if not smartLimitDate:
            continuer = False #on arrête dès maintenant si pas smart
        elif quantity > 7 and (itemWithData in numberTimeItemWithAttributesSold and quantity >= len(numberTimeItemWithAttributesSold[itemWithData]) / 40):
            continuer = False #on s'arrête si on retourne +20 élément et + de 40eme des ventes dernieres 24h
        elif timestampMinActu <= timestampMin:
            continuer = False #on s'arrête si le timestamp actu est inférieur au minimum
        elif smartLimitDate and itemId in itemsAffectedTemporarely and timestampMinActu <= tempsActu - itemsAffectedTemporarely[itemId][0]:
            log(f"Arrêt de la recup d'intervalle de temps suite à itemsAffectedTemporarely {itemId} (pas une erreur)")
            continuer = False
        else:
            timestampMinActu -= 900 #on élargit de 15 min
            timestampMax += 900

    if returnTimestampMinAndAuctionNumber:
        return aReturn, timestampMinActu, quantity
    return aReturn


async def ajouter_donnee_dans_liste_pour_mediane(valeurAAjouer, liste, profondeurDansLaListe=0):
    i = 0
    if type(valeurAAjouer) == list or type(valeurAAjouer) == tuple:
        valeurAAjouerInt = int(valeurAAjouer[0])
    else:
        valeurAAjouerInt = int(valeurAAjouer)

    if profondeurDansLaListe == 0:
        while i < len(liste) and valeurAAjouerInt > int(liste[i]):
            i += 1
    elif profondeurDansLaListe == 1:
        while i < len(liste) and valeurAAjouerInt > int(liste[i][0]):
            i += 1
    else:
        await alerte_strasky_serv("ajouter_donnee_dans_liste_pour_mediane() : profondeur non gérée")
    liste.insert(i, valeurAAjouer)
    return liste

def dico_to_tuple(dico): #profondeur jusqu'à 3
    aReturn = []
    a = list(dico.items())
    for ia in range(len(dico)):
        if type(a[ia][1]) == dict:
            aReturn.append([a[ia][0], []]) #pour avoir sous la forme [key, [values]]
            b = list(a[ia][1].items())
            for ib in range(len(a[ia][1])):
                if type(b[ib][1]) == dict:
                    aReturn[ia][1].append([b[ib][0], []]) #pour avoir sous la forme [key, [values]]
                    c = list(b[ib][1].items())
                    for ic in range(len(b[ib][1])):
                        if type(c[ic][1]) == dict:
                            aReturn[ia][1][ib][1].append([c[ic][0], []]) #pour avoir sous la forme [key, [values]]
                            d = list(c[ic][1].items())
                            for id in range(len(c[ic][1])):
                                if type(d[id][1]) == dict:
                                    log("Dict trop profond (dico_to_tuple)")
                                    log(f"Avec {dico}")
                                    exit()
                                else:
                                    aReturn[ia][1][ib][1][ic][1].append(d[id])

                            aReturn[ia][1][ib][1][ic][1] = tuple(aReturn[ia][1][ib][1][ic][1])
                            aReturn[ia][1][ib][1][ic] = tuple(aReturn[ia][1][ib][1][ic])
                        else:
                            aReturn[ia][1][ib][1].append(c[ic])
                    aReturn[ia][1][ib][1] = tuple(aReturn[ia][1][ib][1])
                    aReturn[ia][1][ib] = tuple(aReturn[ia][ib])
                else:
                    aReturn[ia][1].append(b[ib])
            aReturn[ia][1] = tuple(aReturn[ia][1])
            aReturn[ia] = tuple(aReturn[ia])
        else:
            aReturn.append(a[ia])
    aReturn = tuple(aReturn)
    return aReturn

async def gerer_les_donnees_item(auction):
    nbtData = nbt.nbt.NBTFile(fileobj=io.BytesIO(base64.b64decode(auction["item_bytes"])))
    extraAttributes = nbtData["i"][0]["tag"]["ExtraAttributes"]

    isDungeonItem = False
    if "DUNGEON" in nbtData["i"][0]["tag"]["display"]["Lore"][-1]:
        isDungeonItem = True

    if "dungeon_item_level" in extraAttributes:  # si l'item a des stars
        dungeonItemLvl = extraAttributes["dungeon_item_level"].value
    else:
        dungeonItemLvl = 0

    if "modifier" in extraAttributes:  # si l'item est reforge
        reforge = extraAttributes["modifier"].value
    else:
        reforge = None

    if "enchantments" in extraAttributes:  # si l'item est enchanté
        enchants = []
        for enchantActu in extraAttributes["enchantments"].items():
            enchants.append((enchantActu[0], enchantActu[1].value))  # sous la forme (enchant, valeur)
    else:
        enchants = []

    if "runes" in extraAttributes:  # si l'item est enchanté
        runes = {}
        for runeActu in extraAttributes["runes"].items():
            runes[runeActu[0]] = runeActu[1].value
    else:
        runes = {}
    if "rarity_upgrades" in extraAttributes:
        rarityUpgrades = extraAttributes["rarity_upgrades"].value
    else:
        rarityUpgrades = 0

    donneesAdditionnelles = {}
    itemId = extraAttributes["id"].value
    if itemId == "PET":
        donneesAdditionnelles["pet_info"] = {}
        donneesJSON = json.load(io.StringIO(extraAttributes["petInfo"].value))
        donneesAdditionnelles["pet_info"]["type"] = donneesJSON["type"]
        if "heldItem" in donneesJSON:
            donneesAdditionnelles["pet_info"]["held_item"] = donneesJSON["heldItem"]
        else:
            donneesAdditionnelles["pet_info"]["held_item"] = None
        if "skin" in donneesJSON:
            donneesAdditionnelles["pet_info"]["skin"] = donneesJSON["skin"]
        else:
            donneesAdditionnelles["pet_info"]["skin"] = None
        if "candy_used" in donneesJSON:
            donneesAdditionnelles["pet_info"]["candy_used"] = donneesJSON["candyUsed"]
        else:
            donneesAdditionnelles["pet_info"]["candy_used"] = 0

        try:
            indexLettreActu = 5
            while auction["item_name"][indexLettreActu + 1] != "]":  # pour récupérer le level
                indexLettreActu += 1
            donneesAdditionnelles["pet_info"]["level"] = int(auction["item_name"][5:indexLettreActu + 1])
        except:
            await alerte_strasky_serv(f"Erreur dans gerer_donnees_items, list index out of range ? lors de la définition du level d'un pet : {auction['item_name']}")

    '''for i in extraAttributes.items():
        if i[0] not in listeTemp and "DRILL" in itemId:
            log(i[0] + ", " + auction["item_name"] + "  :  " + str(i[1].value) + "  ,  " + extraAttributes["id"].value + "   :")
            for b in auction.items():
                log(b, end=" | ")
            log("")
            log("---------")
            listeTemp.append(i[0])'''
    if "wood_singularity_count" in extraAttributes:
        donneesAdditionnelles["wood_singularity_count"] = extraAttributes["wood_singularity_count"].value
    if "hot_potato_count" in extraAttributes:
        donneesAdditionnelles["hot_potato_count"] = extraAttributes["hot_potato_count"].value
    if "ability_scroll" in extraAttributes:
        donneesAdditionnelles["ability_scroll"] = extraAttributes["ability_scroll"].value
    if "spider_kills" in extraAttributes:
        donneesAdditionnelles["spider_kills"] = extraAttributes["spider_kills"].value
    if "zombiesKilled" in extraAttributes:
        donneesAdditionnelles["zombiesKilled"] = extraAttributes["zombiesKilled"].value
    if "skin" in extraAttributes:
        donneesAdditionnelles["skin"] = extraAttributes["skin"].value
    if "talisman_enrichment" in extraAttributes:
        donneesAdditionnelles["talisman_enrichment"] = extraAttributes["talisman_enrichment"].value
    if "drill_part_upgrade_module" in extraAttributes:
        donneesAdditionnelles["drill_part_upgrade_module"] = extraAttributes["drill_part_upgrade_module"].value
    if "drill_part_fuel_tank" in extraAttributes:
        donneesAdditionnelles["drill_part_fuel_tank"] = extraAttributes["drill_part_fuel_tank"].value
    if "drill_part_engine" in extraAttributes:
        donneesAdditionnelles["drill_part_engine"] = extraAttributes["drill_part_engine"].value
    if "drill_fuel" in extraAttributes:
        donneesAdditionnelles["drill_fuel"] = extraAttributes["drill_fuel"].value

    return {
        "auctioneer": auction["auctioneer"],
        "start": auction["start"],
        "end": auction["end"],
        "item_name": auction["item_name"],
        "item_id": itemId,
        "category": auction["category"],
        "tier": auction["tier"],
        "starting_bid": auction["starting_bid"],
        "count": nbtData["i"][0]["Count"].value,
        "dungeon_item_level": dungeonItemLvl,
        "reforge": reforge,
        "enchs": tuple(enchants),
        "runes": runes,
        "rarity_upgrades": rarityUpgrades,
        "donnees_additionnelles": donneesAdditionnelles,
        "lastUpdated": lastHypixelApiUpdate,
        "dungeon_item": isDungeonItem
    }
async def fonction_annexe_pour_trouver_mediane_avec_limite_temps(var, timestampMin, smartLimitDate, timestampRLePlusPetit, isGetPrixReforge=False, itemWithData=None):
    itemId = None
    if itemWithData is not None:
        itemId = itemWithData[4:]
    if isGetPrixReforge:
        if var[1] not in tiers_reforgeables:
            await alerte_strasky_serv(f"Le tier {var[1]} est inconnu")
            return None
        donneesApresLimiteTemps, timestampActu, quantity = await recuperer_uniquement_donnee_selon_intervalle_de_temps(
            dataReforgesPrices[var[0]], timestampMin,
            smartLimitDate=smartLimitDate,
            returnTimestampMinAndAuctionNumber=True,
            itemId=itemId, itemWithData=itemWithData)
    else:
        donneesApresLimiteTemps, timestampActu, quantity = await recuperer_uniquement_donnee_selon_intervalle_de_temps(
        var, timestampMin,
        smartLimitDate=smartLimitDate,
        returnTimestampMinAndAuctionNumber=True,
        itemId=itemId, itemWithData=itemWithData)

    if len(donneesApresLimiteTemps) < 1: #si on a pas de données
        return None, timestampRLePlusPetit, 0

    if timestampActu < timestampRLePlusPetit:
        timestampRLePlusPetit = timestampActu


    if isGetPrixReforge:
        return await trouver_mediane(donneesApresLimiteTemps, 1, True) * tiers_reforgeables[var[1]], timestampRLePlusPetit, quantity
    return await trouver_mediane(donneesApresLimiteTemps, 1, True), timestampRLePlusPetit, quantity

async def algo_trouver_prix_attributs(attributs, uniquementEstimerPrix=False, retournerFiabilite=False, *, returnAllPrices=False, smartLimitDate=False, returnTimestampMini=False, timestampMin=0):
    #TODO finir de gérer les enchants pour les dungeon items
    if len(attributs) != 11: #débugage
        await alerte_strasky_serv(f"algo_trouver_prix_attributs : taille des attributs != 11  : {attributs}")
    prixTrouves = [] #sous la forme attributs (index), médiane, quantity
    prixManquants = [] #liste des ids (leur index dans attributs) manquants
    stars = attributs[3]
    moinsFiable = [999999999, (None,), 0] #l'attribut le moins fiable sous la forme quantité de données, indexDansPrixTrouves, prix
    complexe = False
    '''if smartLimitDate:
        timestampMin = round(get_current_utc_timestamp()) - 14400 #la date la + veille max (4h de base)'''
    timestampRLePlusPetit = 999999999999999

    try:
        complexe = hypixelAlias[attributs[0][4:]][1]
    except:
        log(f"Aucun alias pour {attributs[0]} (découpé comme {attributs[0][4:]})")

    if complexe == False:
        if attributs[0] in hypixelDataPrices and hypixelDataPrices[attributs[0]] != []:
            resultatMediane, timestampRLePlusPetit, quantity = await fonction_annexe_pour_trouver_mediane_avec_limite_temps(hypixelDataPrices[attributs[0]], timestampMin, smartLimitDate, timestampRLePlusPetit, False, attributs[0])
            if resultatMediane == None:
                prixManquants.append((0,))
            else:
                prixTrouves.append(((0,), resultatMediane[0], quantity))
                moinsFiable = await modifier_moins_fiable(moinsFiable, resultatMediane, (0,))
        else:
            prixManquants.append((0,))
    #index 1 : le tier : ignoré
    #la rarity upgrade : IGNORE (remplacé par le tier index devant le nom de l'item)
    #index 3 : les stars IGNORE

    if attributs[4] != None:
        if attributs[4] in dataReforgesPrices: #les reforges
            if attributs[1] == "SUPREME":
                await alerte_strasky_serv("Item tier SUPREME reforge, skipping item")
                log("Item tier SUPREME reforge, skipping item")
                if uniquementEstimerPrix:
                    aReturn = [None]
                    if retournerFiabilite:
                        aReturn.append(None)
                    if returnAllPrices:
                        aReturn.append(None)
                    if returnTimestampMini:
                        aReturn.append(None)
                    return aReturn
                return #si on voulait trouver le prix, pas besoin de return une var
            try:
                resultatMediane, timestampRLePlusPetit, quantity = await fonction_annexe_pour_trouver_mediane_avec_limite_temps((attributs[4], attributs[1]), timestampMin, smartLimitDate, timestampRLePlusPetit, True)
            except:
                log(f"Erreur algo_trouver_prix_attributs : reforges : {attributs}")
                await alerte_strasky_serv(f"Erreur algo_trouver_prix_attributs : reforges : {attributs}")
            if resultatMediane == None:
                prixManquants.append((4,))
            else:
                prixTrouves.append(((4,), resultatMediane[0], quantity))
                moinsFiable = await modifier_moins_fiable(moinsFiable, resultatMediane, (4,))
        else:
            prixManquants.append((4,))

    if attributs[0][4:] != "ENCHANTED_BOOK":
        for enchIndex in range(len(attributs[5])): #les enchants
            #TODO modifier la valeur en fonction du nombre d'enchants
            key = f"{attributs[5][enchIndex][1]}L{attributs[5][enchIndex][0]}"  # donne 1LProtection pour protection 1
            ench_hash = await du.get_first_layer_attributes_hash(key)

            if attributs[0][4:] in items_dungeon_enchanted: #est un item dungeon potentiellement drop enchant
                if ench_hash in dataEnchants[1]:
                    resultatMediane, timestampRLePlusPetit, quantity = await fonction_annexe_pour_trouver_mediane_avec_limite_temps(dataEnchants[1][ench_hash], timestampMin, smartLimitDate, timestampRLePlusPetit)
                    if resultatMediane == None:
                        prixManquants.append((5, enchIndex))
                    else:
                        prixTrouves.append(((5, enchIndex), resultatMediane[0], quantity))
                        moinsFiable = await modifier_moins_fiable(moinsFiable, resultatMediane, (5, enchIndex))
                else:
                    prixManquants.append((5, enchIndex))
            else: #si pas item dungeon potentiellement drop enchant
                if ench_hash in dataEnchants[0]:
                    resultatMediane, timestampRLePlusPetit, quantity = await fonction_annexe_pour_trouver_mediane_avec_limite_temps(dataEnchants[0][ench_hash], timestampMin, smartLimitDate, timestampRLePlusPetit)
                    if resultatMediane == None:
                        prixManquants.append((5, enchIndex))
                    else:
                        prixTrouves.append(((5, enchIndex), resultatMediane[0], quantity))
                        moinsFiable = await modifier_moins_fiable(moinsFiable, resultatMediane, (5, enchIndex))
                else:
                    prixManquants.append((5, enchIndex))

    for runeIndex in range(len(attributs[6])): #les runes
        key = f"{attributs[6][runeIndex][1]}L{attributs[6][runeIndex][0]}"  # donne 1LFire Spiral pour Fire Spiral Rune lvl 1
        if key in dataAttributesPrices:
            resultatMediane, timestampRLePlusPetit, quantity = await fonction_annexe_pour_trouver_mediane_avec_limite_temps(dataAttributesPrices[key], timestampMin, smartLimitDate, timestampRLePlusPetit)
            if resultatMediane == None:
                prixManquants.append((6, runeIndex))
            else:
                prixTrouves.append(((6, runeIndex), resultatMediane[0], quantity))
                moinsFiable = await modifier_moins_fiable(moinsFiable, resultatMediane, (6, runeIndex))
        else:
            prixManquants.append((6, runeIndex))

    if attributs[7] != (): #les données additionnelles
        #pour les pets
        if attributs[0][2:] == "PET":
            for i in range(len(attributs[7][0][1])):
                if attributs[7][0][1][i][1] != 0 and attributs[7][0][1][i][1] != None:
                    typeWithTier = attributs[0][:2] + attributs[7][0][1][0][1]
                    key = str(attributs[7][0][1][i][0]) + ":" + str(attributs[7][0][1][i][1])
                    if attributs[7][0][1][i][0] == "level":
                        if attributs[7][0][1][i][1] >= 10: #évite si level < 20
                            typeWithLevelAndTier = f"{typeWithTier}{attributs[7][0][1][i][0]}:{round(attributs[7][0][1][i][1]/5)*5}" #met le type avec le level arrondi à 5 près
                            if typeWithLevelAndTier in dataPetsPrices:
                                resultatMediane, timestampRLePlusPetit, quantity = await fonction_annexe_pour_trouver_mediane_avec_limite_temps(
                                    dataPetsPrices[typeWithLevelAndTier], timestampMin, smartLimitDate, timestampRLePlusPetit)
                                if resultatMediane == None:
                                    prixManquants.append((7, 0, 1, i))
                                else:
                                    prixTrouves.append(((7, 0, 1, i), resultatMediane[0], quantity))
                                    moinsFiable = await modifier_moins_fiable(moinsFiable, resultatMediane, (7, 0, 1, i))
                            else:
                                prixManquants.append((7, 0, 1, i))

                    elif attributs[7][0][1][i][0] == "type":
                        key = f"type:{typeWithTier}"
                        if key in dataPetsPrices:
                            resultatMediane, timestampRLePlusPetit, quantity = await fonction_annexe_pour_trouver_mediane_avec_limite_temps(
                                dataPetsPrices[key], timestampMin, smartLimitDate,
                                timestampRLePlusPetit)
                            if resultatMediane == None:
                                prixManquants.append((7, 0, 1, i))
                            else:
                                prixTrouves.append(((7, 0, 1, i), resultatMediane[0], quantity))
                                moinsFiable = await modifier_moins_fiable(moinsFiable, resultatMediane, (7, 0, 1, i))
                        else:
                            prixManquants.append((7, 0, 1, i))
                    elif key in dataPetsPrices:
                        resultatMediane, timestampRLePlusPetit, quantity = await fonction_annexe_pour_trouver_mediane_avec_limite_temps(
                            dataPetsPrices[key], timestampMin, smartLimitDate,
                            timestampRLePlusPetit)
                        if resultatMediane == None:
                            prixManquants.append((7, 0, 1, i))
                        else:
                            prixTrouves.append(((7, 0, 1, i), resultatMediane[0], quantity))
                            moinsFiable = await modifier_moins_fiable(moinsFiable, resultatMediane, (7, 0, 1, i))

                    else:
                        prixManquants.append((7, 0, 1, i))

        else: #pour les non pets
            if attributs[7][0][1] != 0 and attributs[7][0][1] != None or len(attributs[7]) > 1: #ou si il y a plusieurs valeurs dans le tuple
                key = f"{attributs[7][0][0]}:{attributs[7][0][1]}"
                if key in dataDonneesAdditionnellesPrices:
                    resultatMediane, timestampRLePlusPetit, quantity = await fonction_annexe_pour_trouver_mediane_avec_limite_temps(
                        dataDonneesAdditionnellesPrices[key], timestampMin, smartLimitDate,
                        timestampRLePlusPetit)
                    if resultatMediane == None:
                        prixManquants.append((7,))
                    else:
                        prixTrouves.append(((7,), resultatMediane[0], quantity))
                        moinsFiable = await modifier_moins_fiable(moinsFiable, resultatMediane, (7,))
                else:
                    prixManquants.append((7,))
    #l'index 10 à gerer: si c'est un dungeon item

    #l'algo de prix
    totalPrixTrouves = 0
    for i in prixTrouves:
        totalPrixTrouves += i[1]

    prixAttributManquant = attributs[9] - totalPrixTrouves #le prix de vente - le total des prix trouvés
    if prixAttributManquant < 0:
        prixAttributManquant = 0

    if retournerFiabilite and uniquementEstimerPrix == False:
        await alerte_strasky_serv("algo_trouver_prix_attributs : retournerFiabilite demandé sans uniquementEstimerPrix")
    if returnAllPrices and uniquementEstimerPrix == False:
        await alerte_strasky_serv("algo_trouver_prix_attributs : returnAllPrices demandé sans uniquementEstimerPrix")

    if uniquementEstimerPrix:
        if len(prixManquants) == 0:
            aReturn = [totalPrixTrouves]
            if retournerFiabilite:
                aReturn.append(moinsFiable[0])
            if returnAllPrices:
                aReturn.append(prixTrouves)
            if returnTimestampMini:
                aReturn.append(timestampRLePlusPetit)

        else:
            aReturn = [None]
            if retournerFiabilite:
                aReturn.append(None)
            if returnAllPrices:
                aReturn.append(None)
            if returnTimestampMini:
                aReturn.append(None)
        return aReturn

    elif len(prixManquants) == 1: #si il ne manque qu'un prix
        if prixManquants[0][0] == 4:  # si reforge
            prixAttributManquant = await get_prix_reforge_pour_common(prixAttributManquant, attributs[1])
        await ajouter_un_prix_d_un_attribut(attributs, prixManquants[0], complexe, prixAttributManquant)

    elif len(prixManquants) == 0: #si on a déjà tous les prix estimés
        #on va recalculer la valeur la moins fiable (celle avec le moins de données pour la médiane)
        prixEstimeViaCetteVente = attributs[9] - (totalPrixTrouves - moinsFiable[2])
        if moinsFiable[1][0] == 4:  # si reforge
            prixEstimeViaCetteVente = await get_prix_reforge_pour_common(prixEstimeViaCetteVente, attributs[1])

        await ajouter_un_prix_d_un_attribut(attributs, moinsFiable[1], complexe, prixEstimeViaCetteVente)
    '''if attributs[0] == "PET":
        log(f"Toutes les infos du pet : {attributs}")
        log(f"Ses prix manquants {prixManquants}")'''

async def modifier_moins_fiable(moinsFiable, resultatMediane, index):
    if resultatMediane[1] < moinsFiable[0]:
        return [resultatMediane[1], index, resultatMediane[0]]
    else:
        return moinsFiable

async def ajouter_un_prix_d_un_attribut(attributs, index, complexe, prixAAjouter):
    stars = attributs[3]
    if index[0] == 0 and complexe == False:  # si item
        if attributs[0] not in hypixelDataPrices:
            hypixelDataPrices[attributs[0]] = []
        hypixelDataPrices[attributs[0]] = await ajouter_donnee_dans_liste_pour_mediane((prixAAjouter, round(get_current_utc_timestamp())), hypixelDataPrices[attributs[0]], 1)

    elif index[0] == 4:  # si reforge
        if attributs[4] not in dataReforgesPrices:
            dataReforgesPrices[attributs[4]] = []
        dataReforgesPrices[attributs[4]] = await ajouter_donnee_dans_liste_pour_mediane((prixAAjouter, round(get_current_utc_timestamp())), dataReforgesPrices[attributs[4]], 1)

    elif index[0] == 5:  # si enchant
        if attributs[0][4:] != "ENCHANTED_BOOK":
            key = f"{attributs[5][index[1]][1]}L{attributs[5][index[1]][0]}" #donne 1LProtection pour protection 1
            ench_hash = await du.get_first_layer_attributes_hash(key)

            if attributs[0][4:] in items_dungeon_enchanted:
                if ench_hash not in dataEnchants[1]:
                    dataEnchants[1][ench_hash] = []
                dataEnchants[1][ench_hash] = await ajouter_donnee_dans_liste_pour_mediane((prixAAjouter, round(get_current_utc_timestamp())), dataEnchants[1][ench_hash], 1)
            else:
                if ench_hash not in dataEnchants[0]:
                    dataEnchants[0][ench_hash] = []
                dataEnchants[0][ench_hash] = await ajouter_donnee_dans_liste_pour_mediane((prixAAjouter, round(get_current_utc_timestamp())), dataEnchants[0][ench_hash], 1)

    elif index[0] == 6:  # si rune
        key = f"{attributs[6][index[1]][1]}L{attributs[6][index[1]][0]}"  # donne 1LFire Spiral pour Fire Spiral Rune lvl 1
        if key not in dataAttributesPrices:
            dataAttributesPrices[key] = []
        dataAttributesPrices[key] = await ajouter_donnee_dans_liste_pour_mediane((prixAAjouter, round(get_current_utc_timestamp())), dataAttributesPrices[key], 1)

    elif index[0] == 7:  # si donnée additionnelle
        if attributs[0][2:] == "PET":
            typeWithTier = str(tier_to_index[attributs[1]]) + "T" + attributs[7][0][1][0][1]
            actu = attributs[7][0][1][index[3]]

            if index[3] == 4: #si c'est un level
                actu = (typeWithTier + attributs[7][0][1][4][0], round(attributs[7][0][1][4][1]/5)*5)#met le type avec le level arrondi à 5 près

            elif index[3] == 0: #si c'est un type de pet
                actu = (attributs[7][0][1][0][0], typeWithTier)

            if type(actu) == tuple or type(actu) == list:
                if len(actu) != 2: #débugage
                    await alerte_strasky_serv("ajouter_un_prix_d_un_attribut : Pour donnée additionnelle pet : actu != 2")
                    log(f"{attributs}, actu = {actu}")
                    await alerte_strasky_serv(f"{attributs}, actu = {actu}")
                actu = f"{actu[0]}:{actu[1]}"

            if actu not in dataPetsPrices:
                dataPetsPrices[actu] = []
            dataPetsPrices[actu] = await ajouter_donnee_dans_liste_pour_mediane((prixAAjouter, round(get_current_utc_timestamp())), dataPetsPrices[actu], 1)
        else: #si pas pet
            strDesDonneesAdditionnelles = ""
            for d in attributs[7]:
                if type(d) == tuple or type(d) == list:
                    if len(d) != 2: #Débugage
                        await alerte_strasky_serv("ajouter_un_prix_d_un_attribut : Pour donnée additionnelle non pet : dans le for d in attributs[7], d != 2")
                        log(attributs)
                        await alerte_strasky_serv(f"{attributs}")
                    strDesDonneesAdditionnelles += f"{d[0]}:{d[1]}|"
                else:
                    log("ajouter_un_prix_d_un_attribut : Pour donnée additionnelle non pet : dans le for d in attributs[7], d n'est ni tuple ni list")
                    await alerte_strasky_serv("ajouter_un_prix_d_un_attribut : Pour donnée additionnelle non pet : dans le for d in attributs[7], d n'est ni tuple ni list")
            if len(strDesDonneesAdditionnelles) > 1:
                strDesDonneesAdditionnelles = strDesDonneesAdditionnelles[:-1] #pour enlever le dernier "|"

            if strDesDonneesAdditionnelles not in dataAttributesPrices:
                dataAttributesPrices[strDesDonneesAdditionnelles] = []
            dataAttributesPrices[strDesDonneesAdditionnelles] = await ajouter_donnee_dans_liste_pour_mediane((prixAAjouter, round(get_current_utc_timestamp())), dataAttributesPrices[strDesDonneesAdditionnelles], 1)

async def get_prix_reforge(reforge, tier):
    if tier not in tiers_reforgeables:
        await alerte_strasky_serv(f"Le tier {tier} est inconnu")
        return None
    try:
        result = await trouver_mediane(dataReforgesPrices[reforge], 1, True)
        return result[0] * tiers_reforgeables[tier], result[1]
    except:
        await alerte_strasky_serv("Erreur fatale dans get_prix_reforge, il semblerait que le prix de la reforge ne soit pas dans la base de données")
        return None

async def get_prix_reforge_pour_common(prix, tier):
    if tier not in tiers_reforgeables:
        await alerte_strasky_serv(f"Le tier {tier} est inconnu")
        return None
    try:
        return prix / tiers_reforgeables[tier]
    except:
        await alerte_strasky_serv("Erreur fatale dans get_prix_reforge, il semblerait que le prix de la reforge ne soit pas dans la base de données")
        return None

async def get_attributs_pour_estimation_prix(auction, tupleAuction=True):
    if tupleAuction:
        return [str(tier_to_index[auction[1]['tier']]) + "T" + str(auction[1]["dungeon_item_level"]) + "S" + auction[1]["item_id"],
                auction[1]["tier"],
                auction[1]["rarity_upgrades"],
                auction[1]["dungeon_item_level"],
                auction[1]["reforge"],
                auction[1]["enchs"],
                dico_to_tuple(auction[1]["runes"]),
                dico_to_tuple(auction[1]["donnees_additionnelles"]),
                auction[1]["end"],
                auction[1]["starting_bid"] / auction[1]["count"],
                auction[1]["dungeon_item"]
                ]
    else:
        return [str(tier_to_index[auction['tier']]) + "T" + str(auction["dungeon_item_level"]) + "S" + auction["item_id"],
                auction["tier"],
                auction["rarity_upgrades"],
                auction["dungeon_item_level"],
                auction["reforge"],
                auction["enchs"],
                dico_to_tuple(auction["runes"]),
                dico_to_tuple(auction["donnees_additionnelles"]),
                auction["end"],
                auction["starting_bid"] / auction["count"],
                auction["dungeon_item"]
                ]
async def sauvegarde_dans_db():
    global soldHistoryAlreadySent
    if is_nightly:
        return
    log("sauvegarde en cours")

    await dbtools.modify_data_into_db("hypixelDataPrices", generer_string_dune_var(hypixelDataPrices))

    await dbtools.modify_data_into_db("dataAttributesPrices", generer_string_dune_var(dataAttributesPrices))

    await dbtools.modify_data_into_db("dataReforgesPrices", generer_string_dune_var(dataReforgesPrices))

    await dbtools.modify_data_into_db("dataDonneesAdditionnellesPrices", generer_string_dune_var(dataDonneesAdditionnellesPrices))

    await dbtools.modify_data_into_db("dataPetsPrices", generer_string_dune_var(dataPetsPrices))

    await dbtools.modify_data_into_db("numberTimeItemWithAttributesSold", generer_string_dune_var(numberTimeItemWithAttributesSold))

    await dbtools.modify_data_into_db("playersData", generer_string_dune_var(playersData))

    await dbtools.modify_data_into_db("stats", generer_string_dune_var(bot_stats))

    if not soldHistoryAlreadySent:
        log("ajout du nouveau soldHistory")
        await dbtools.save_into_data_db(generer_string_dune_var(soldHistory), f"soldHistory{lastSoldHistoryId+1}")
        soldHistoryAlreadySent = True
    else:
        await dbtools.modify_data_into_db(f"soldHistory{lastSoldHistoryId+1}", generer_string_dune_var(soldHistory))

async def data_cleanup():
    global hypixelDataPrices, dataAttributesPrices, dataReforgesPrices
    tabPricesVars = [hypixelDataPrices, dataAttributesPrices, dataReforgesPrices]
    for var in tabPricesVars:
        for key, data in var.items():
            for vente in data:
                if vente[1] < get_current_utc_timestamp() - 604_800:
                    var[key].remove(vente)

async def get_event_api():
    r = []
    session = aiohttp.ClientSession()
    rJSON = None
    async with session.get("https://api.tftech.de/Event") as resp:
        rJSON = await resp.json()
    if rJSON == None:
        await alerte_strasky_serv("get_event_api : impossible de charger la page/le json")
        await session.close()
        return {}
    await session.close()
    result = {}
    for event in rJSON:
        if event["end"] is not None and event["priority"] == "HIGH":
            r.append(event["name"])

    return r

log(f"avant vars {process.memory_info().rss / 1024 ** 2}")

hypixelAlias = {}  # sous la forme "id de l'item": ["nom de l'item", complexe=False]
traductions = {} #sous la forme nom_message:{lang1: traduction1, ...}
helps = {} #sous la forme commande: {"desc": {langues}, "example": {langues}}
items_linked_events = {} #sous la forme event: [liste des items_id]

alertsByItemId = {}

with open("data/alias.json", "r") as f:
    hypixelAlias = json.load(f)

with open("data/traductions.json", "r", -1, "utf-8") as f:
    traductions = json.load(f)

with open("data/help.json", "r", -1, "utf-8") as f:
    helps = json.load(f)

with open("data/items_linked_events.json") as f:
    items_linked_events = json.load(f)

with open("data/events.json") as f:
    events_timings_data = json.load(f)

with open("data/dungeon-enchanted-items.json") as f:
    items_dungeon_enchanted = tuple(json.load(f))

next_events = {}

show_ram = False

hypixelApiDataViaUUID = {}

hypixelDataPrices = {}  # sous la forme {"item_name": [[prix, timesptamp]]} classé par ordre croissant, on ne garde que 48h de données

#coupleItemsEtAttributsAvecPrix = {}  # sous la forme {item, attribut1, attribut2, ...}: [(prix, timesptamp)]

firstLayerHashDict = {}

dataEnchants = [{}, {}] #[dict_items_normaux, dict_items_dungeon] avec pour les dict en clé le firstLayerHashDict

dataAttributesPrices = {}  # sous la forme attribut: [[prix, timestamp], ...] classé par ordre croissant
dataReforgesPrices = {} #sous la forme reforge: [[prix, timesptamp], ...] classé par ordre croissant PRIX pour la rarity COMMON
dataDonneesAdditionnellesPrices = {} #sous la forme (tuple contenant toutes les donnees additionnelles): prix
dataPetsPrices = {} #sous la forme (type, valeur) : prix

soldHistory = {} #"hash_de_litem": [[prix, timesptamp], ...]
lastSoldHistoryId = None
soldHistoryAlreadySent = False
oldSoldHistory = {}

dataPrices = {} #tous les prix sous la forme index_dattribut: {"valeur_attribut": [[prix, timestamp]]}

guildsData = {} #sous la forme guild:{param:value, ...}
playersData = {} #sous la forme player:{param:value, ...}
events = []

#TODO gérer dataDonneesAdditionnellesPrices et dataPetsPrices (dans cleanup et pour remplir ces variables)

numberTimeItemWithAttributesSold = {} #sous la forme item_id: [timestamp1, timestamp2, ...]

itemsAffectedTemporarely = {} #sous la forme item_id: [écart_de_timestamp_a_utiliser, timestamp_péremption] (si écart de timestamp == None, item à ignorer)
itemBans = {} #idItem: [Timestamp_début_ban, niveau]

leaks = [] #sous la forme [content, timestamp, attached_image]
news = [] #sous la forme [content, timestamp, attached_image]

maintenance = False
arreter = False
timestampDemarrage = get_current_utc_timestamp() # en sec
aliasManquants = {}  # temp sous la forme "id": ["possibilité de nom1", "possibilité de nom2", ...]
auctionsInteressantes = {}  # l'uuid de l'auction: les messages [id_channel, id_message], profit(str)]

donators = []
upHistory = []

bot_stats = {}# statistique: valeur

banLevels = {0: 0, 1: 900, 2: 2700, 3: 7200, 4: 21600}

starsList = ["",
             "✪",
             "✪✪",
             "✪✪✪",
             "✪✪✪✪",
             "✪✪✪✪✪"]
tier_to_index = {
    "COMMON": 1,
    "UNCOMMON": 2,
    "RARE": 3,
    "EPIC": 4,
    "LEGENDARY": 5,
    "MYTHIC": 6,
    "SUPREME": 7,
    "SPECIAL": 8,
    "VERY_SPECIAL": 9
}

index_to_tier = (None, "COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY", "MYTHIC", "SUPREME", "SPECIAL", "VERY_SPECIAL")

tempsDeRafraichissementDeLApi = 60
redemarrerAlias = False
guildsDataModified = False
playersDataModified = False
isStonksEnabled = True
stonksAlert = True
speedUpdate = False

if time.timezone == -3600:
    log("UTC+1, activation de speedUpdate")
    speedUpdate = True

#récupération des variables présentes dans la db:
conn_db = sqlite3.connect("/home/ubuntu/pythonDB.db")
cursor = conn_db.cursor()
cursor.execute("SELECT value FROM data WHERE key = 'hypixelDataPrices'")

value = cursor.fetchone()
if value != None:
    hypixelDataPrices = generer_var_dun_string(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'dataAttributesPrices'")

value = cursor.fetchone()
if value != None:
    dataAttributesPrices = generer_var_dun_string(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'dataReforgesPrices'")

value = cursor.fetchone()
if value != None:
    dataReforgesPrices = generer_var_dun_string(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'dataDonneesAdditionnellesPrices'")

value = cursor.fetchone()
if value != None:
    dataDonneesAdditionnellesPrices = generer_var_dun_string(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'dataPetsPrices'")

value = cursor.fetchone()
if value != None:
    dataPetsPrices = generer_var_dun_string(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'guildsData'")
value = cursor.fetchone()
if value != None:
    guildsData = generer_var_dun_string(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'numberTimeItemWithAttributesSold'")
value = cursor.fetchone()
if value != None:
    numberTimeItemWithAttributesSold = generer_var_dun_string(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'leaks'")
value = cursor.fetchone()
if value != None:
    leaks = json.loads(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'news'")
value = cursor.fetchone()
if value != None:
    news = json.loads(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'playersData'")
value = cursor.fetchone()
if value != None:
    playersData = generer_var_dun_string(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'stats'")
value = cursor.fetchone()
if value != None:
    bot_stats = generer_var_dun_string(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'donators'")
value = cursor.fetchone()
if value != None:
    donators = generer_var_dun_string(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'dataEnchants'")
value = cursor.fetchone()
if value != None:
    dataEnchants = generer_var_dun_string(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'firstLayerHashDict'")
value = cursor.fetchone()
if value != None:
    firstLayerHashDict = generer_var_dun_string(value[0])


cursor.execute("SELECT value FROM data WHERE key = 'lastSoldHistoryId'")
value = cursor.fetchone()
if value != None:
    lastSoldHistoryId = int(value[0])
else:
    log("Erreur : pas de lastSoldHistoryId trouvée")
    exit()

cursor.execute(f"SELECT value FROM data WHERE key = 'soldHistory{lastSoldHistoryId}'")
value = cursor.fetchone()
if value != None:
    oldSoldHistory = generer_var_dun_string(value[0])

cursor.execute(f"SELECT value FROM data WHERE key = 'upHistory'")
value = cursor.fetchone()
if value != None:
    upHistory = json.loads(value[0])

cursor.execute("SELECT value FROM data WHERE key = 'maintenance'")
value = cursor.fetchone()
if value != None:
    maintenance = json.loads(value[0])
else:
    log("impossible de récupérer l'état de maintenance")

if is_nightly:
    maintenance = True
    log("Activation maintenance suite à mode nightly")
cursor.close()
conn_db.close()

#débugage
a = [hypixelDataPrices, dataAttributesPrices, dataPetsPrices, dataReforgesPrices, dataDonneesAdditionnellesPrices]
for i in a:
    for ii in i.items():
        for iii in ii[1]: #les tabs de prix
            if iii[1] > get_current_utc_timestamp():
                log(f"erreur débugage récup données : \n{i}\n{ii}\n{iii}")
for i in numberTimeItemWithAttributesSold.items(): #débugage + clear des vielles ventes
    nvTab = []
    for ii in i[1]:
        if ii > get_current_utc_timestamp():
            log(f"erreur débugage récup données : \n{i}\n{ii}")
        if ii > get_current_utc_timestamp() - 86400:  # si - de 24h
            nvTab.append(ii)
    numberTimeItemWithAttributesSold[i[0]] = nvTab

log("Lancement du fichier")
log(f"après vars {process.memory_info().rss / 1024 ** 2}")

async def traiter_donnees_API():
    nbRuns = 0
    session = aiohttp.ClientSession()
    await client.wait_until_ready()

    global last_api_process
    last_api_process = None

    global maintenance, is_nightly
    if maintenance:
        await modify_state("maintenance")
        log("Le bot est en maintenance")
    #log(await get_event_api())

    global leaks, news
    tabLeaksAndNews = [{"var": leaks, "var_name": "leaks", "channel_id": 845351604001439765, "function": add_leaks},
                       {"var": news, "var_name": "news", "channel_id": 842482146928099350, "function": add_news}]
    # pour récupérer les leaks et les news
    for i in tabLeaksAndNews:
        counter = 0
        async for message in client.get_guild(842453728154091561).get_channel(i["channel_id"]).history(limit=99999999):
            counter += 1
        if i["var"] == None or counter > len(i["var"]):
            log("Nouveaux leaks/news détectés")
            async for message in client.get_guild(842453728154091561).get_channel(i["channel_id"]).history(
                    limit=99999999):
                existeDeja = False
                timestamp = round(message.created_at.timestamp())
                for b in i["var"]:
                    if b[0] == message.content and b[1] == timestamp:
                        existeDeja = True
                if not existeDeja:
                    await i["function"](message)

    await data_cleanup()

    timestampDepuisPriceRefresh = get_current_utc_timestamp()
    timestampDepuisAuctionsClear = timestampDepuisPriceRefresh
    global arreter, show_ram
    global lastHypixelApiUpdate, playersDataModified, soldHistory, lastSoldHistoryId, soldHistoryAlreadySent, hypixel_token_used_history, auctionsInteressantes, dataEnchants
    global aliasManquants, hypixelAlias, guildsDataModified, isStonksEnabled, stonksAlert, itemsAffectedTemporarely, bot_stats, discordStatus, hypixelApiDataViaUUID


    lastHypixelApiUpdate = None
    timeout = aiohttp.ClientTimeout(total=4)

    log("Démarrage de la récupération des données dans 2 secondes")
    await asyncio.sleep(2)
    #log(lastSoldHistoryId)
    if not is_nightly: #on incrémente
        await dbtools.modify_data_into_db('lastSoldHistoryId', str(lastSoldHistoryId + 1))

    while arreter == False:
        if show_ram or is_nightly: log(f"avant run {nbRuns} {process.memory_info().rss / 1024 ** 2}")
        if nbRuns == 1 and not is_nightly:
            await client.get_channel(811605424935403560).send(content=f"{client.get_guild(727239318602514526).get_role(834456742640877580).mention} Le bot est lancé !")
        nbRuns += 1
        log(f"Démarrage de la run {nbRuns} après la synchro")

        upHistory.append(round(time.time()))
        if not is_nightly:
            await dbtools.modify_data_into_db('upHistory', json.dumps(upHistory))

        nbPages, lastHypixelApiUpdate, hypixel_token_used_history, auctionsInteressantes = await wait_until_hypixel_api_refresh(nbRuns, lastHypixelApiUpdate, hypixel_token_used_history, auctionsInteressantes)

        log("Synchro")

        page = 0
        await client.change_presence(status=discordStatus,
                                     activity=discord.Game(f"{texteDefaultActivity} - Getting and analyzing Hypixel's Data - Run {nbRuns}"))
        sessionIsStonks = aiohttp.ClientSession()
        if speedUpdate:
            nbPages = 3
        auctionsADelete = []
        dictAvecTemps = {}
        current_events_run = current_events(events_timings_data)
        for event in current_events_run:
            await add_items_linked_with_event_in_itemsAffectedTemporarely(event[0], event[1])

        if timestampDepuisAuctionsClear + 1200 < get_current_utc_timestamp(): #on clear les auctions terminées toutes les 20 minutes
            clear_des_auctions_cette_run = True
        else:
            clear_des_auctions_cette_run = False
        
        while page < nbPages:  # les auctions terminées ne sont pas référencés, pour savoir si elle est terminée il faut regarder si elle est encore dans la liste, et vérifier que ce n'est pas une annulation de l'auctioneer

            try:
                reponseJSON = None
                async with session.get(url + "auctions", params={"page": page}, timeout=timeout) as resp:
                    reponseJSON = await resp.json()
            except Exception as ex:
                log(f"erreur lors du chargement de la page {page} : {ex} ")
                await alerte_strasky_serv(f"erreur lors du chargement de la page {page} : voir erreur console")


            if reponseJSON is None:
                log(f"La page {page} n'a pas été chargée (ReponseJSON is None)")
                await alerte_strasky_serv(f"La page {page} n'a pas été chargée (ReponseJSON is None)")
            elif reponseJSON["success"] == True:
                nbPages = reponseJSON["totalPages"]
                for auction in reponseJSON["auctions"]:
                    if "bin" in auction and auction["item_name"] != "null":
                        if auction["uuid"] not in hypixelApiDataViaUUID:
                            #t = time.time()
                            hypixelApiDataViaUUID[auction["uuid"]] = await gerer_les_donnees_item(auction)

                            # pour les alias
                            auctionVar = hypixelApiDataViaUUID[auction["uuid"]]
                            if auctionVar["item_id"] not in hypixelAlias:
                                if auctionVar["item_id"] not in aliasManquants:
                                    aliasManquants[auctionVar["item_id"]] = []
                                if auctionVar["item_name"] not in aliasManquants[auctionVar["item_id"]]:
                                    aliasManquants[auctionVar["item_id"]].append(auctionVar["item_name"])
                                    await client.get_channel(834375906683912202).send(
                                        f"L'item {auctionVar['item_name']} ayant pour id {auctionVar['item_id']} n'est pas dans la base de données alias\n`\"{auctionVar['item_id']}\": [\"{auctionVar['item_name']}\", false, {round(time.time())}]`")

                            # pour si stonks
                            #log(f"avant stonks {(time.time() - t)*1000}ms")
                            idAvecTierEtStars = str(tier_to_index[auctionVar["tier"]]) + "T" + str(auctionVar["dungeon_item_level"]) + "S" + auctionVar["item_id"]

                            if idAvecTierEtStars in hypixelDataPrices and len(
                                    hypixelDataPrices[idAvecTierEtStars]) > 0 and \
                                    auction[
                                        "uuid"] not in auctionsInteressantes and isStonksEnabled:  # si l'item est dans la base des prix et pas déjà alerté et is_stonks activé
                                is_stonksResultat = await is_stonks(auctionVar, sessionIsStonks, auction["uuid"], nbRuns)
                                if is_stonksResultat[0] and stonksAlert: #si c'est stonks et que les alertes stonks activées
                                    messages = []

                                    for i in is_stonksResultat[1]:
                                        messages.append([i[1], (await client.get_channel(i[1]).send(content=i[0], embed=i[2])).id])
                                    auctionsInteressantes[auction["uuid"]] = [messages, is_stonksResultat[2], auction["item_name"], auction["start"]//1000]
                                    #log(f"après stonks affiché {(time.time() - t) * 1000}ms")
                            """try:
                                dictAvecTemps[auctionVar["item_id"]] = [dictAvecTemps[auctionVar["item_id"]][0] + (time.time() - t)*1000, dictAvecTemps[auctionVar["item_id"]][1] + 1]
                            except:
                                dictAvecTemps[auctionVar["item_id"]] = [(time.time() - t)*1000, 1]"""

                        elif clear_des_auctions_cette_run:
                            hypixelApiDataViaUUID[auction["uuid"]]["lastUpdated"] = lastHypixelApiUpdate

                    '''if auction["end"] < lastHypixelApiUpdate:
                        log(
                            f"Erreur d'Hypixel : L'auction {auction['uuid']} semble être terminée (timestamp<ApiLastUpdated) !")'''
                        #await alerte_strasky_serv(
                        #    f"Erreur d'Hypixel : L'auction {auction['uuid']} semble être terminée (timestamp<ApiLastUpdated) !")
                        # temp:

                if speedUpdate:
                    log(
                        f"{reponseJSON['page']}/{nbPages} at {datetime.fromtimestamp(get_current_utc_timestamp())} (lastUpdate = {datetime.fromtimestamp(lastHypixelApiUpdate / 1000)}) ")

            else:
                await alerte_strasky_serv(f"Erreur : page {page} success = False")
            if speedUpdate:
                nbPages = 3
            page += 1
            await asyncio.sleep(0.08)

        await sessionIsStonks.close()
        log("fin du traitement des nouvelles auctions")
        '''dictAAfficher = {}
        for i in dictAvecTemps.items():
            dictAAfficher[i[0]] = i[1][0]/i[1][1]
        log(dictAAfficher)'''

        #si lastUpdated n'existe pas
        try:
            if reponseJSON["lastUpdated"] != lastHypixelApiUpdate:
                await alerte_strasky_serv(f"La lastUpdated actuelle ne correspond pas à la lastHypixelApiUpdate")
        except:
            pass
            #await alerte_strasky_serv("Erreur lastUpdated n'existe pas")
            #await alerte_strasky_serv(reponseJSON)
        temp = 0
        temp2 = 0
        supValue = [0] * 7  # 5k, 50k, 100k, 200k, 400k, 500k, 1m

        if show_ram or is_nightly: log(f"avant récup terminées run {nbRuns} {process.memory_info().rss / 1024 ** 2}")

        if nbRuns > 1:
            async with session.get(url + "auctions_ended") as resp:
                respJSON = await resp.json()
                for auction in respJSON["auctions"]:
                    if "bin" in auction and auction["bin"]:
                        skipping = False

                        # on considère que ces items ont étés vendus

                        #pour enregistrer dans couplePrixItemsEtAttributs:
                        if auction["auction_id"] in hypixelApiDataViaUUID:
                            attributsActus = await get_attributs_pour_estimation_prix(hypixelApiDataViaUUID[auction["auction_id"]], False)

                            item_hash = await du.get_attributes_hash(attributsActus)

                            auctionsADelete.append([auction["auction_id"], auction["buyer"], auction[
                                "timestamp"] // 1000])  # ajoute l'auction à la liste à supprimer

                            # pour trouver le prix de l'item / d'attributs
                            await algo_trouver_prix_attributs(attributsActus)

                            try:
                                numberTimeItemWithAttributesSold[attributsActus[0]].append(
                                    round(get_current_utc_timestamp()))
                            except:
                                numberTimeItemWithAttributesSold[attributsActus[0]] = [
                                    round(get_current_utc_timestamp())]

                            try:
                                soldHistory[item_hash].append((attributsActus[9], round(time.time())))
                            except:
                                soldHistory[item_hash] = [(attributsActus[9], round(time.time()))]


        if clear_des_auctions_cette_run: 
            log("lancement d'un clear (items vendus, pour les 2 variables)")
            for auction in hypixelApiDataViaUUID.items():
                if auction[1]["lastUpdated"] < lastHypixelApiUpdate - 61:
                    auctionsADelete.append([auction[0], None, None])
            for itemWithAttributesSold in numberTimeItemWithAttributesSold.items():
                nvTab = []
                for timestamp in itemWithAttributesSold[1]:
                    if timestamp > get_current_utc_timestamp() - 86400: #si - de 24h
                        nvTab.append(timestamp)
                numberTimeItemWithAttributesSold[itemWithAttributesSold[0]] = nvTab

            timestampDepuisAuctionsClear = get_current_utc_timestamp()

        log(f"{len(auctionsADelete)} {len(hypixelApiDataViaUUID)}")
        for auction_actu in auctionsADelete:  #supprime les auctions terminées
            try:
                hypixelApiDataViaUUID.pop(auction_actu[0])
            except:
                pass
            if auction_actu[0] in auctionsInteressantes and auction_actu[1] is not None:
                messages = auctionsInteressantes.pop(auction_actu[0])
                player_name = await get_player_name_by_api(auction_actu[1], session)
                for message_data_actu in messages[0]:
                    try:
                        message_actu = await client.get_channel(message_data_actu[0]).fetch_message(message_data_actu[1])
                        await message_actu.edit(embed=await generer_embed(None, messages[2], f"__**SOLD**__ *in {round(auction_actu[2] - messages[3])}s*, for {messages[1][0]} estimated profit ({messages[1][1]}%)\nBought by `{player_name}`",
                                                                          thumbnail="https://media.discordapp.net/attachments/811611272251703357/850051408782819368/sold-stamp.jpg",
                                                                          color=0xe62e00))
                    except:
                        log("impossible de modifier une auction vendue")


        auctionsADelete = []

        if nbRuns % 3 == 0 and not speedUpdate: #toutes les 3 runs on sauvegarde
            await data_cleanup()
            await sauvegarde_dans_db()
            #on vérifie si le bot va devoir s'éteindre prochainement
            '''struct_time = datetime.fromtimestamp(get_current_utc_timestamp()).timetuple()
            if struct_time[3] == 0:
                await modify_state("offline")'''
        if not is_nightly:
            if guildsDataModified:
                log("Sauvegarde des données des guilds")
                await dbtools.modify_data_into_db("guildsData", generer_string_dune_var(guildsData))
                guildsDataModified = False
            if playersDataModified:
                log("Sauvegarde des données des joueurs")
                await dbtools.modify_data_into_db("playersData", generer_string_dune_var(playersData))
                playersDataModified = False

        try:
            for i in itemsAffectedTemporarely.items():
                if i[1][1] != None and i[1][1] < get_current_utc_timestamp():
                    await alerte_strasky_serv(f"Fin de l'affectation temporaire de l'item {i[0]}")
                    itemsAffectedTemporarely.pop(i[0])
        except:
            log("itemsAffectedTemporarely clear skipped (bug handled)")
        last_api_process = get_current_utc_timestamp()
        if show_ram or is_nightly: log(f"après run {nbRuns} {process.memory_info().rss / 1024 ** 2}")

        if nbRuns % 400 == 0 and not is_nightly: #si on a dépassé les 400 runs
            log("Reset le soldHistory")
            await dbtools.modify_data_into_db(f"soldHistory{lastSoldHistoryId}", generer_string_dune_var(soldHistory))
            soldHistory = {}
            soldHistoryAlreadySent = False
            lastSoldHistoryId += 1
            await dbtools.modify_data_into_db('lastSoldHistoryId', str(lastSoldHistoryId + 1))



    await session.close()
    log("fin traitement API")
    await alerte_strasky_serv("La routine de traitement de l'API s'arrête")
    exit()



async def gerer_les_alias():
    log("alias editing activé")
    await client.wait_until_ready()

    global redemarrerAlias, aliasManquants
    while len(aliasManquants) < 1:
        await asyncio.sleep(10)

    while True:
        listeAliasManquantsTemp = aliasManquants.items()
        listeAliasManquants = []
        for i in listeAliasManquantsTemp:  # pour si le dict change de taille
            listeAliasManquants.append(i)
        listeAliasManquants = tuple(listeAliasManquants)

        if len(listeAliasManquants) > 0:
            for i in listeAliasManquants:
                await client.get_channel(815499113004793916).send("--------------------------")
                nbPossibilites = len(i[1])
                if nbPossibilites > len(listeDesEmojis):
                    await client.get_channel(815499113004793916).send("Toutes les possibilités ne sont pas affichées")
                    nbPossibilites = len(listeDesEmojis)

                aEnvoyer = f"L'item ayant pour id **{i[0]}** n'a pas de nom, lui donner comme nom "

                for b in range(nbPossibilites):
                    aEnvoyer += f"\n - \"{i[1][b]}\" : {listeDesEmojis[b]}"
                aEnvoyer += "\nCliquez sur :x: pour skip l'item"
                aEnvoyer += "\nCliquez sur ❗ si cet item est complexe (avant les autres réactions)"
                aEnvoyer += "\nSi le nom de l'item voulu n'est pas dans la liste, écrivez le dans le channel (:warning: attention aux majuscules et aux espaces, il faut avoir vraiment le bon nom)"
                envoi = await client.get_channel(815499113004793916).send(aEnvoyer)

                for b in range(nbPossibilites):
                    await envoi.add_reaction(listeDesEmojis[b])
                await envoi.add_reaction("❌")
                await envoi.add_reaction("❗")
                reactions = envoi.channel.last_message.reactions
                reactionNotChanged = True
                choix = None
                while reactionNotChanged and envoi.id == envoi.channel.last_message_id:
                    await asyncio.sleep(2)
                    if redemarrerAlias == True:
                        break
                    for reactionIndex in range(len(reactions)):
                        if reactions[
                            reactionIndex].count > 1 and reactionIndex <= nbPossibilites:  # pour pas si complexe
                            reactionNotChanged = False
                            choix = reactionIndex

                if redemarrerAlias == True:
                    break
                complexe = False
                if reactions[len(reactions) - 1].count > 1:
                    complexe = True

                if choix != None and choix < nbPossibilites:  # pour pas que ce soit via une réponse textuel ou un skip
                    hypixelAlias[i[0]] = [i[1][choix], complexe]
                    await client.get_channel(815499113004793916).send(
                        f"Choix validé : '{i[1][choix]}' complexe={complexe}!")
                    try:
                        aliasManquants[i[0]].pop()
                    except:
                        log("Erreur de pop")
                elif choix == None:
                    hypixelAlias[i[0]] = [str(envoi.channel.last_message.content), complexe, round(time.time())]
                    await client.get_channel(815499113004793916).send(
                        f"Choix validé : {str(envoi.channel.last_message.content)} complexe={complexe}!")
                    try:
                        aliasManquants[i[0]].pop()
                    except:
                        log("Erreur de pop")

            redemarrerAlias = False
        else:
            await asyncio.sleep(30)


async def routine_verif_crash():
    await asyncio.sleep(60)
    global last_api_process, arreter
    while not arreter:
        if last_api_process is not None and last_api_process + 600 < time.time():
            await alerte_strasky_serv("La routine de traitement de l'API semble avoir crash (pas d'update depuis 5 min), essai de redémarrage de celle-ci <@399978674578784286>")
            log("La routine de traitement de l'API semble avoir crash (pas d'update depuis 5 min), essai de redémarrage de celle-ci")
            loop_traiter_donnees_api.stop()
            loop_traiter_donnees_api.start()
        await asyncio.sleep(30)

# time.time() en s et hypixel timestamp en ms
loop_alias = discord.ext.tasks.Loop(gerer_les_alias, 0, 0, 0, None, True, client.loop)

'''loop_traiter_donnees_api = discord.ext.tasks.Loop(traiter_donnees_API, 0, 0, 0, None, True, client.loop)

loop_routine_verif_crash = discord.ext.tasks.Loop(routine_verif_crash, 0, 0, 0, None, True, client.loop)

if not speedUpdate:
    loop_traiter_donnees_api.start()
    loop_routine_verif_crash.start()
else:
    log("SpeedUpdate -> ne lance pas l'api")

async def t():
    print("coucou")

def q():
    asyncio.run(traiter_donnees_API)

async def main():
    print("starting gather")
    await asyncio.gather(
        t(),
        asyncio.to_thread(q),
        client.run(TOKEN)
    )
asyncio.run(main())'''
#client.run(TOKEN)

loop = asyncio.get_event_loop()

async def run_bot():
    try:
        await client.start(TOKEN)
    except Exception:
        print("Le client a eu une issue !")
        await client.close()

def run_in_thread():
    fut = asyncio.run_coroutine_threadsafe(traiter_donnees_API(), loop)
    fut.result()  # wait for the result


async def main():
    print("Starting gather")
    await asyncio.gather(
        asyncio.to_thread(run_in_thread),
        run_bot()
    )
    log("fin du main")


loop.run_until_complete(main())
log("fin du programme")
