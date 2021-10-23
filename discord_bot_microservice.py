import discord, discord.ext.tasks
from discord_bot_microservice_utils.logs_obj import init_a_new_logger
from microservices_utils.objs import Microservice, MicroserviceReceiver, MicroserviceSender, Queue
from discord_bot_microservice_utils.others_objs import GlobalDBM, AlertChannel, AlertRole, Guild, timestamp_to_pretty_hour
import threading
import discord_bot_microservice_utils.commands as discord_commands
import discord_bot_microservice_utils.internal_microservices_commands as internal_microservices_commands
from time import sleep, time
from datetime import datetime
import asyncio
from json import load
from logging import INFO, StreamHandler, getLogger, Formatter, FileHandler
from sys import stdout
import aiohttp
import os

client = discord.Client()

MICROSERVICE_NAME = "discord_bot"
MICROSERVICE_PREFIX = "D"

try:
    TOKEN = os.environ["TOKEN"]
    print("Started in Normal Mode")
    NIGHTLY_MODE = False
except:
    TOKEN = "ODUxMDQzNTA2NjU5MjYyNDg0.YLyiBw._wW_KwuGd8FUMUIS15dVx3Xs3NA"
    print("Started in Nightly Mode")
    NIGHTLY_MODE = True

file_handler_discord_py = FileHandler(filename='/home/ubuntu/logs/discord.log', encoding='utf-8', mode='a')

file_handler_discord_py.setLevel(INFO)

formatter_discord_py = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler_discord_py.setFormatter(formatter_discord_py)

logger_discord_py = getLogger('discord')
logger_discord_py.setLevel(INFO)
logger_discord_py.addHandler(file_handler_discord_py)

stdout_handler_discord_py = StreamHandler(stdout)
stdout_handler_discord_py.setFormatter(formatter_discord_py)
logger_discord_py.addHandler(stdout_handler_discord_py)

microservice = Microservice(MICROSERVICE_NAME, MICROSERVICE_PREFIX, {"discord_client": client})
microservice_sender = MicroserviceSender(microservice, init_a_new_logger("Microservice sender DBM"))

commands = discord_commands.DiscordCommands(client, microservice)

queue_to_execute = Queue(init_a_new_logger("Execution queue obj - DBM"))

async def wait_for_execute():
    await client.wait_until_ready()
    while GlobalDBM.run:
        await asyncio.sleep(0.1)
        if len(queue_to_execute.queue) > 0:
            data_to_exec = queue_to_execute.get_prior_and_delete_it()
            await data_to_exec["command"](data_to_exec["args"], microservice)

def listening_to_main_microservices_serv():
    logger = init_a_new_logger("Socket listening DBM")
    logger.warning("listening_to_main_microservices_serv started")
    
    while GlobalDBM.run:
        receiver = MicroserviceReceiver(microservice, logger)
        logger.info(f"new MicroserviceReceiver created for {microservice.name} microservice")
        sleep(0.1)
        if not receiver.connection_alive:
            sleep(1)
        while receiver.connection_alive:
            req = receiver.listen()
            if req is None:
                break #connection closed, not alive anymore
            if req["command"] in internal_microservices_commands.text_to_command:
                queue_to_execute.add(req["args"]["request_id"], {"command": internal_microservices_commands.text_to_command[req["command"]], "args": req["args"]})
            else:
                logger.error(f"Got a request with a command not in text_to_command : {req}")

async def scan_for_ended_auctions():
    logger = init_a_new_logger("Scan for ending auctions DBM")
    logger.info("Started scan_for_ended_auctions")

    while GlobalDBM.run:
        uuids_to_pop = []
        logger.debug("restarting the loop in scan_for_ended_auctions")
        async with aiohttp.ClientSession() as session:
            for auctions_list_index in range(len(GlobalDBM.auctions_to_scan_list)-1, -1, -1):
                auction_uuid = GlobalDBM.auctions_to_scan_list[auctions_list_index]
                alert_messages_data = GlobalDBM.auctions_to_scan_for_solding_with_uuid_and_alert_message_id[auction_uuid]
                await asyncio.sleep(0.8)
                async with session.get('https://api.hypixel.net/skyblock/auction', params={"key": "21b31128-0fea-4f43-8452-6e972445df38", "uuid": auction_uuid}) as req:
                    if req.status != 200:
                        logger.warning(f"req for auction uuid page finished with code {req.status} for auction uuid {auction_uuid}")
                    else:
                        json_data = await req.json()
                        if json_data["success"] != True:
                           logger.warning(f"req for auction uuid page hasn't been successful for auction uuid {auction_uuid}")
                        else:
                            if len(json_data["auctions"]) < 1 or json_data["auctions"][0]["end"]/1000 < time():
                                for channel_id, message_id in alert_messages_data:
                                    channel = client.get_channel(channel_id)
                                    
                                    message = await channel.fetch_message(message_id)
                                    embed = message.embeds[0]
                                    if len(json_data["auctions"]) > 0:
                                        embed.title = f'[SOLD in {round(json_data["auctions"][0]["end"]/1000 - json_data["auctions"][0]["start"]/1000)} seconds] ' + embed.title
                                    else:
                                        embed.title = "[SOLD] " + embed.title
                                    embed.set_thumbnail(url="https://media.discordapp.net/attachments/811611272251703357/850051408782819368/sold-stamp.jpg")
                                    access_field = embed.fields[8].value
                                    access_field = access_field[1:-1].split("\n")
                                    access_field = [access_field[0][:-1], access_field[1][1:]]
                                    access_field = "\n".join(access_field)
                                    embed.set_field_at(8, name=embed.fields[8].name, value="~~" + access_field + "~~")
                                    embed.colour = 0xff0000
                                    await message.edit(embed=embed)
                                    uuids_to_pop.append(auction_uuid)
                                    """except:
                                        logger.warning(f"Exception occured while fetching message or modifying it")"""
            for uuid in uuids_to_pop:
                try:
                    GlobalDBM.auctions_to_scan_for_solding_with_uuid_and_alert_message_id.pop(uuid)
                except:
                    logger.info(f"Error when trying to delete uuid {uuid} from GlobalDBM.auctions_to_scan_for_solding_with_uuid_and_alert_message_id")
                try:
                    GlobalDBM.auctions_to_scan_list.pop(GlobalDBM.auctions_to_scan_list.index(uuid))
                except:
                    logger.info(f"Error when trying to delete uuid {uuid} from GlobalDBM.auctions_to_scan_list")
            await asyncio.sleep(8)
        

#to change for dynamic alerts

if NIGHTLY_MODE:
    alert_channels = {
        849910024423866398: AlertChannel(849910024423866398, 100_000, 0.1, 999999999999, 9999999999),
        891251073925406730: AlertChannel(891251073925406730, 100_000, 0.1, 999999999999, 9999999999)
    }
else:
    alert_channels = {
        857696959791235092: AlertChannel(857696959791235092, 100_000, 0.1, 999999999999, 9999999999), #all-flips
        857301519531114546: AlertChannel(857301519531114546, 100_000, 0.1, 1_000_000, 9999999999), #low-flips
        857301677850099722: AlertChannel(857301677850099722, 1_000_000, 0.1, 99999999999, 9999999999) #high-flips
    }

Guild(842453728154091561, alert_channels_by_id=alert_channels,
alert_roles_by_id={
    890651386721734666: AlertRole(890651386721734666, 100_000, 0.20, 999999999999, 9999999999, 1), #100k
    842686623313690695: AlertRole(842686623313690695, 250_000, 0.15, 999999999999, 9999999999, 1), #250k
    842686927362719755: AlertRole(842686927362719755, 500_000, 0.10, 999999999999, 9999999999, 1), #500k
    842686965010530305: AlertRole(842686965010530305, 1_000_000, 0.10, 999999999999, 9999999999, 1), #1m
    842686999352705094: AlertRole(842686999352705094, 2_000_000, 0.10, 999999999999, 9999999999, 1), #2m
    842687033523568649: AlertRole(842687033523568649, 5_000_000, 0.10, 999999999999, 9999999999, 1), #5m

    850810432330924072: AlertRole(850810432330924072, 200_000, 0.25, 999999999999, 9999999999, 2), #25%
    850810532377133066: AlertRole(850810532377133066, 200_000, 0.50, 999999999999, 9999999999, 2), #50%
    850810660866228274: AlertRole(850810660866228274, 200_000, 0.75, 999999999999, 9999999999, 2), #75%
    850810759801864202: AlertRole(850810759801864202, 200_000, 1, 999999999999, 9999999999, 2), #100%
    850810814859575346: AlertRole(850810814859575346, 200_000, 2, 999999999999, 9999999999, 2) #200%
})

process_listening = threading.Thread(target=listening_to_main_microservices_serv)
process_listening.start()

listening_loop = discord.ext.tasks.Loop(wait_for_execute, 0, 0, 0, None, True, client.loop)
listening_loop.start()

scan_for_ended_auctions_loop = discord.ext.tasks.Loop(scan_for_ended_auctions, 0, 0, 0, None, True, client.loop)
scan_for_ended_auctions_loop.start()

client.run(TOKEN)