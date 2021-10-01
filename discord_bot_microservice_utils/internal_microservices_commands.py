try:
    from discord_bot_microservice_utils.logs_obj import init_a_new_logger
    from discord_bot_microservice_utils.others_objs import generate_embed, pretty_number, Guild, GlobalDBM, timestamp_to_pretty_hour
    from discord_bot_microservice_utils.commands import AwaitedRequest
except:
    from logs_obj import init_a_new_logger
    from others_objs import generate_embed, pretty_number, Guild, GlobalDBM, timestamp_to_pretty_hour
    from commands import AwaitedRequest

import asyncio, aiohttp
from discord import Embed, Game, Status
from time import time
from discord_slash.utils.manage_components import create_actionrow, create_select, create_select_option, wait_for_component

URL_API_TO_USERNAME = "https://minecraft-api.com/api/pseudo/"
MAX_PURPOSES_FOR_ITEM_NAME = 20

logger = init_a_new_logger("Internal microservices commands - DBM")

emojis_list = [
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
        attributes += f"\n**Reforge:** {item_data['reforge']['name']} estimated at {pretty_number(item_data['reforge']['estimation'])} *on {pretty_number(item_data['reforge']['sold_amount'], 1)} sales*"
    if "enchants" in item_data:
        attributes += "\n\n**Enchantments:**"
        for enchant in item_data["enchants"]:
            attributes += f" {enchant['name']} ({pretty_number(enchant['estimation'])}) +"
        attributes = attributes[:-2] #to delete the last " +"
        if item_data["enchants_type"] != None:
            if item_data["enchants_type"] == 1:
                attributes += "(specified for dungeon item which can be dropped enchanted)"
            elif item_data["enchants_type"] == 2:
                attributes += "(specified for an enchanted book)"
        else:
            logger.warning("Got a stonks alert with item_data['enchants_type'] is None")
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

    embed = generate_embed(
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
            roles_to_ping_by_groups = {} #group_id: role_obj
            for alert_role in tuple(guild.alert_roles_by_id.values()):
                if alert_role.is_this_must_be_alerted(absolute_profitability, relative_profitability):
                    #to ping only 1 role for each group
                    if alert_role.group in roles_to_ping_by_groups:
                        if roles_to_ping_by_groups[alert_role.group].absolute_min_to_alert < alert_role.absolute_min_to_alert:
                            roles_to_ping_by_groups[alert_role.group] = alert_role #this role has a higher absolute min so we alert this one
                        
                        elif roles_to_ping_by_groups[alert_role.group].absolute_min_to_alert == alert_role.absolute_min_to_alert:
                            if roles_to_ping_by_groups[alert_role.group].relative_min_to_alert < alert_role.relative_min_to_alert:
                                roles_to_ping_by_groups[alert_role.group] = alert_role #this role has a higher % min so we alert it
                    else:
                        roles_to_ping_by_groups[alert_role.group] = alert_role
            
            embed_color_with_group = [0xffffff, 9999] #color, group, the lowest group id is the best
            guild_discord_obj = microservice.useful_objs["discord_client"].get_guild(guild.guild_id)
            for group, role in roles_to_ping_by_groups.items():
                str_roles_to_ping += f"<@&{role.role_id}> "
                if group < embed_color_with_group[1]:
                    embed_color_with_group = [guild_discord_obj.get_role(role.role_id).colour.value, group]
            
            for alert_channel in tuple(guild.alert_channels_by_id.values()):
                if alert_channel.is_this_must_be_alerted(absolute_profitability, relative_profitability):
                    channel = microservice.useful_objs["discord_client"].get_channel(alert_channel.channel_id)
                    if channel is None:
                        logger.debug(f"Channel with id {alert_channel.channel_id} in guild {guild.guild_id} is None when getting it")
                    else:
                        if str_roles_to_ping == "> ": #won't create a content in the message
                            await channel.send(embed=embed)
                        else:
                            embed.colour = embed_color_with_group[0]
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

async def cmd_resp_search_item_name(args, microservice):
    if args["request_id"] not in AwaitedRequest.request_id_to_obj:
        logger.error("request id not found in AwaitedRequest.request_id_to_obj in funct cmd_resp_search_item_name")
        return

    awaited_request = AwaitedRequest.request_id_to_obj.pop(args["request_id"])
    ctx = awaited_request.args["ctx"]
    if args["status"] == "NOTHING FOUND":
        await ctx.send(":x: No item found")
    elif args["status"] == "NOTHING ACCURATE":
        await ctx.send(":x: Nothing accurate found")
    elif args["status"] == "MULTIPLE FOUND":
        await ctx.send(f"Found multiple results : {args['found_names']}")
    elif args["status"] == "OK":
        await ctx.send(f"Item found : {args['found_name']}")
    else:
        await ctx.send(":x: Internal error : bad status")
        logger.error("bad cmd_resp_search_item_name status")

async def cmd_resp_get_price_with_search_item_name(args, microservice):
    if args["request_id"] not in AwaitedRequest.request_id_to_obj:
        logger.error("request id not found in AwaitedRequest.request_id_to_obj in funct cmd_resp_search_item_name")
        return

    awaited_request = AwaitedRequest.request_id_to_obj[args["request_id"]]
    ctx = awaited_request.args["ctx"]
    title = ""
    description = ""
    fields = []
    thumbnail = None
    action_row = None
    if args["status"] == "NOTHING FOUND":
        title = "Item not found"
        description = "Sorry, we haven't found any corresponding item to your request"
        thumbnail = "https://media.discordapp.net/attachments/811611272251703357/861271094458712064/error_v2.webp?width=677&height=676"
    elif args["status"] == "NOTHING ACCURATE":
        title = "Item not found"
        description = "Sorry, we haven't found an accurate item corresponding to your request"
        thumbnail = "https://media.discordapp.net/attachments/811611272251703357/861271094458712064/error_v2.webp?width=677&height=676"
    elif args["status"] == "MULTIPLE FOUND":
        title = "Doubt on the item"
        description = "Several items corresponding to your request have been found\n\nPlease select the good one"
        thumbnail = "https://media.discordapp.net/attachments/811611272251703357/833036031413714954/question-mark-1750942_1280.png?width=676&height=676"
        if len(args["found_names"]) > MAX_PURPOSES_FOR_ITEM_NAME: args["found_names"] = args["found_names"][:MAX_PURPOSES_FOR_ITEM_NAME]
        options = [create_select_option(found_name, found_name) for found_name in args["found_names"]]
        action_row = create_actionrow(create_select(options))
    else:
        await ctx.send(":x: Internal error : bad status")
        logger.error("bad cmd_resp_search_item_name status")
        return
    embed = generate_embed(title, description, fields=fields, thumbnail=thumbnail)
    if action_row is None: 
        await ctx.send(embed=embed)
    else:
        #means we've had to choose between item names
        await ctx.send(embed=embed, components=[action_row])
        option_ctx = await wait_for_component(microservice.useful_objs["discord_client"], components=action_row)
        embed = generate_embed(title, f"You've chosed {option_ctx.selected_options[0]}", fields=fields, thumbnail=thumbnail)
        await option_ctx.edit_origin(embed=embed, components=[])
        if not hasattr(microservice, "sender"):
            await ctx.send(content=":x: Internal Error: no sender attr, try again in a few minutes")
            logger.error("microservice hasn't sender attr for cmd_resp_get_price_with_search_item_name")
            return
        microservice.sender.send_to_a_microservice(microservice.sender.FIRST_REQUEST, "hypixel_api_analysis", "get_price_with_correct_name", {"item_name": option_ctx.selected_options[0], "intervall": args["intervall"]}, req_id=args["request_id"])

async def cmd_resp_get_price_with_correct_name(args, microservice):
    if args["request_id"] not in AwaitedRequest.request_id_to_obj:
        logger.error("request id not found in AwaitedRequest.request_id_to_obj in funct cmd_resp_get_price_with_correct_name")
        return
    awaited_request = AwaitedRequest.request_id_to_obj.pop(args["request_id"])
    ctx = awaited_request.args["ctx"]
    embed = None
    if args["status"] == "NO ACCURATE SOLD HIST":
        embed = generate_embed("No accurate sold history", 
            "Sorry, we cannot find an accurate sold history for the specified duration, try again with a higher duration (ex: `1w` for 1 week)",
            thumbnail="https://media.discordapp.net/attachments/811611272251703357/861271094458712064/error_v2.webp?width=677&height=676"
        )
    
    elif args["status"] == "IGNORED ITEM":
        embed = generate_embed("Ignored Item", 
            "Sorry, this item is in our list of ignored items, so we cannot give any sold median",
            thumbnail="https://media.discordapp.net/attachments/811611272251703357/861271094458712064/error_v2.webp?width=677&height=676"
        )

    elif args["status"] == "OK":
        stars = "".join(['✪' for i in range(args['dungeon_level'])])
        embed = generate_embed(f"{args['item_name']}{stars}'s price",
            "",
            fields=[
                ["Tier", f"*{args['tier']}*", False],
                ["Intervall used", f"the last {timestamp_to_pretty_hour(args['intervall'])}", False],
                ["Price", f"{pretty_number(args['median_price'])}", True],
                ["Sold amount", f"{pretty_number(args['sold_hist_lenght'])}", True]
            ],
            thumbnail=f"https://sky.lea.moe/item/{args['item_id']}"
        )

    else:
        await ctx.send(":x: Internal error : bad status")
        logger.error("bad cmd_resp_search_item_name status")
        return
    
    await ctx.send(embed=embed)

async def cmd_item_tempban(args, microservice):
    channel = await microservice.useful_objs["discord_client"].fetch_channel(860890262612082708)
    await channel.send(f"Item {args['item_name']} tempbanned for {timestamp_to_pretty_hour(args['duration'])}")

text_to_command = {
    ">send": cmd_send, 
    ">stonks_alert": cmd_stonks_alert,
    ">cur_run_number": cmd_cur_hypixel_api_run_number,
    ">missing_alias": cmd_send_missing_alias,
    ">alive": cmd_alive,
    ">item_tempban": cmd_item_tempban,
    "$search_item_name": cmd_resp_search_item_name,
    "$get_price_with_search_item_name": cmd_resp_get_price_with_search_item_name,
    "$get_price_with_correct_name": cmd_resp_get_price_with_correct_name
}