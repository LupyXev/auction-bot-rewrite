try:
    from discord_bot_microservice_utils.logs_obj import init_a_new_logger
    from discord_bot_microservice_utils.others_objs import generate_embed, pretty_number, Guild, GlobalDBM
except:
    from logs_obj import init_a_new_logger
    from others_objs import generate_embed, pretty_number, Guild, GlobalDBM

import asyncio, aiohttp
from discord import Embed, Game, Status
from time import time

URL_API_TO_USERNAME = "https://minecraft-api.com/api/pseudo/"

logger = init_a_new_logger("Internal microservices commands - DBM")

async def cmd_send(args, microservice):
    print("args got", args)
    """print("channel_id", args["channel_id"])
    channel = microservice.useful_objs["discord_client"].get_channel(811605424935403560)
    print("channel got", channel)
    print("all the channels", microservice.useful_objs["discord_client"].get_all_channels())"""
    channel = microservice.useful_objs["discord_client"].get_channel(args["channel_id"])
    if "content" in args:
        if "embed" in args:
            await channel.send(content=args["content"], embed=Embed.from_dict(args["embed"]))
        else:
            await channel.send(content=args["content"])
    else:
        await channel.send(embed=Embed.from_dict(args["embed"]))

async def cmd_stonks_alert(args, microservice):
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
    absolute_profitability = args["absolute_profitability"]
    relative_profitability = args["relative_profitability"]

    item_data = args["item_data"]
    attributes = f" - This item : {item_data['tier']}, is estimated at {pretty_number(item_data['item_only']['estimation'])} coins *on {pretty_number(item_data['item_only']['sold_amount'], 1)} sales*"
    if "reforge" in item_data:
        attributes += f"\n**Reforge:** {item_data['reforge']['name']} estimated at {pretty_number(item_data['reforge']['estimation'])} *on {pretty_number(item_data['reforge']['sold_amount'], 1)} sales"
    if "enchants" in item_data:
        attributes += "\n\n**Enchantments:**"
        for enchant in item_data["enchants"]:
            attributes += f" {enchant['name']} ({pretty_number(enchant['estimation'])}) +"
        attributes = attributes[:-2] #to delete the last " +"
        if item_data["dungeon_item_which_can_be_drop_enchanted"]:
            attributes += "(specified for dungeon item which can be dropped enchanted)"
    if "runes" in item_data:
        attributes += "\n\n**Rune:**"
        cur_rune_index = 0
        rune_amount = len(item_data["runes"])
        for rune in item_data["runes"]:
            attributes += f" {rune['name']} estimated at {pretty_number(rune['estimation'])} *on {rune['sold_amount']}*"
            cur_rune_index += 1
            if cur_rune_index < rune_amount:
                if cur_rune_index + 1 < rune_amount: #more or 2 runes missing
                    attributes += ", "
                else: #1 rune missing
                    attributes += " and "
    attributes += f"\n\nSold medians are between the {round(args['intervalls_used'][0]/3600, 1)} and {round(args['intervalls_used'][1]/3600, 1)} last hours"

    lowest_bins_message = ""
    cur_index = 0
    lowest_bins_amount = len(args["lowest_bins"])
    if GlobalDBM.cur_hypixel_api_run_number == 0: lowest_bins_message += "||"
    for lowest_bin in args["lowest_bins"]:
        if lowest_bin is None:
            lowest_bins_message += "nothing"
        else:
            lowest_bins_message += pretty_number(lowest_bin)
        cur_index += 1
        if cur_index < lowest_bins_amount:
            if cur_index + 1 < lowest_bins_amount: #more or 2 missing
                lowest_bins_message += ", "
            else:
                lowest_bins_message += " and "
    if GlobalDBM.cur_hypixel_api_run_number == 0: lowest_bins_message += "||"
    
    seller_name = None
    async with aiohttp.ClientSession() as session:
        async with session.get(URL_API_TO_USERNAME + str(args["seller_uuid"]) + "/json") as resp:
            reponseJSON = await resp.json()
            if "pseudo" in reponseJSON:
                seller_name = reponseJSON["pseudo"]

    trust_rate = args["trust_rate"] if args["trust_rate"] <= 1 else 1

    embed = await generate_embed(message=None,
        title=item_data["name"],
        title_description="",
        thumbnail=images_percentage[int(round(trust_rate, 1)*10)]
    )
    embed.add_field(name="**Attributes**", value=attributes, inline=False)
    embed.add_field(name="ㅤ", value="─────────────────", inline=False)
    embed.add_field(name="Buy Price", value=f"{pretty_number(args['buy_price'])}", inline=True)
    embed.add_field(name="Lowest Bins", value=lowest_bins_message, inline=True)
    embed.add_field(name="ㅤ", value="─────────────────", inline=False)
    embed.add_field(name="Potential resell profit", value=f"{pretty_number(args['absolute_profitability'])} ({round(args['relative_profitability']*100)}%)", inline=True)
    embed.add_field(name="Potential resell price", value=f"{pretty_number(args['full_estimation'])}", inline=True)
    embed.add_field(name="ㅤ", value="─────────────────", inline=False)
    embed.add_field(name="Access", value=f"`/ah {seller_name}`\n`/viewauction {args['auction_uuid']}`", inline=False)

    for guild in tuple(Guild.guilds_by_id.values()):
        if len(guild.alert_channels_by_id) > 0:
            str_roles_to_ping = "> "
            for alert_role in tuple(guild.alert_roles_by_id.values()):
                if alert_role.is_this_must_be_alerted(absolute_profitability, relative_profitability):
                    str_roles_to_ping += f"<@&{alert_role.role_id}>"
            
            for alert_channel in tuple(guild.alert_channels_by_id.values()):
                if alert_channel.is_this_must_be_alerted(absolute_profitability, relative_profitability):
                    channel = microservice.useful_objs["discord_client"].get_channel(alert_channel.channel_id)
                    if channel is None:
                        logger.debug(f"Channel with id {alert_channel.channel_id} in guild {guild.guild_id} is None when getting it")
                    else:
                        if str_roles_to_ping == "> ": #won't create a content in the message
                            await channel.send(embed=embed)
                        else:
                            await channel.send(content=str_roles_to_ping, embed=embed)

async def cmd_cur_hypixel_api_run_number(args, microservice):
    await microservice.useful_objs["discord_client"].change_presence(status=Status.online,
        activity=Game(f"Getting/Analysing Hypixel's data - Run {args['run_number']}")
    )
    GlobalDBM.cur_hypixel_api_run_number = args["run_number"]

async def cmd_send_missing_alias(args, microservice):
    await microservice.useful_objs["discord_client"].get_channel(834375906683912202).send(f"`\"{args['item_id']}\": [\"{args['item_name']}\", false, {round(time())}]`")

async def cmd_alive(args, microservice):
    pass

text_to_command = {
    "send": cmd_send, 
    "stonks_alert": cmd_stonks_alert,
    "cur_run_number": cmd_cur_hypixel_api_run_number,
    "missing_alias": cmd_send_missing_alias,
    "alive": cmd_alive
}