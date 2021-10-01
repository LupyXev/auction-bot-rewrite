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

client = discord.Client()

MICROSERVICE_NAME = "discord_bot"
MICROSERVICE_PREFIX = "D"

file_handler_discord_py = FileHandler(filename='./logs/discord.log', encoding='utf-8', mode='a')

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
    logger.info("listening_to_main_microservices_serv started")
    
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

async def event_alerting():
    await client.wait_until_ready()
    logger = init_a_new_logger("Event alerting - DBM")
    events_data = {}
    with open("data/events.json") as f:
        events_data = load(f)
    events_to_alert = ("Spooky Festival", "Winter Island")

    logger.info("started")
    
    while GlobalDBM.run:
        cur_year_start = events_data["start_timestamp"]
        while cur_year_start < time() - events_data["1_year"]:
            cur_year_start += events_data["1_year"]

        channel = client.get_channel(891251073925406730)#TODO change to official channel

        last_message = None
        async for message in channel.history(limit=1):
            last_message = message
        
        for this_event in events_to_alert:
            this_event_data = events_data[this_event]
            if cur_year_start + this_event_data["start"] - this_event_data["gap"] <= time() and\
                cur_year_start + this_event_data["start"] + this_event_data["duration"] >= time():
                #there is an event currently
                
                if this_event not in last_message.content or last_message.created_at.timestamp() < time() - this_event_data["duration"] - this_event_data["gap"]*2:
                    #if the last alert is not for this event
                    time_before_event = cur_year_start + this_event_data["start"] - time()
                    time_before_event_end = cur_year_start + this_event_data["start"] + this_event_data["duration"] - time()
                    end_date = datetime.fromtimestamp(cur_year_start + this_event_data["start"] + this_event_data["duration"])
                    if time_before_event > 0:
                        logger.info("An event incoming detected")
                        await channel.send(f"<@&849292716788940841> **Event {this_event} is coming soon (less than {timestamp_to_pretty_hour(time_before_event)})**\nIt will end in **{timestamp_to_pretty_hour(time_before_event_end)}** (until {end_date} UTC+0)")
                    else:
                        logger.info("An event active detected")
                        await channel.send(f"<@&849292716788940841> **Event {this_event} is currently active**\nIt will end in **{timestamp_to_pretty_hour(time_before_event_end)}** (until {end_date} UTC+0)")

        await asyncio.sleep(120)

#to change for dynamic alerts
Guild(842453728154091561, alert_channels_by_id={
    849910024423866398: AlertChannel(849910024423866398, 100_000, 0.1, 999999999999, 9999999999),
    891251073925406730: AlertChannel(891251073925406730, 100_000, 0.1, 999999999999, 9999999999)
}, alert_roles_by_id={
    890651386721734666: AlertRole(890651386721734666, 100_000, 0.25, 999999999999, 9999999999, 1), #100k
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

event_alerting_loop = discord.ext.tasks.Loop(event_alerting, 0, 0, 0, None, True, client.loop)
event_alerting_loop.start()

listening_loop = discord.ext.tasks.Loop(wait_for_execute, 0, 0, 0, None, True, client.loop)
listening_loop.start()
client.run("ODUxMDQzNTA2NjU5MjYyNDg0.YLyiBw._wW_KwuGd8FUMUIS15dVx3Xs3NA")