import discord, discord.ext.tasks
from discord_bot_microservice_utils.logs_obj import init_a_new_logger
from microservices_utils.objs import Microservice, MicroserviceReceiver, MicroserviceSender, Queue
from discord_bot_microservice_utils.others_objs import GlobalDBM, AlertChannel, AlertRole, Guild
import threading
import discord_bot_microservice_utils.commands as discord_commands
import discord_bot_microservice_utils.internal_microservices_commands as internal_microservices_commands
from time import sleep
import asyncio

client = discord.Client()

MICROSERVICE_NAME = "discord_bot"
MICROSERVICE_PREFIX = "D"

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

#Test
Guild(842453728154091561, alert_channels_by_id={
    849910024423866398: AlertChannel(849910024423866398, 50_000, 0.1, 999999999999, 9999999999)
}, alert_roles_by_id={
    842453728165888018: AlertRole(842453728165888018, 50_000, 0.1, 999999999999, 9999999999)
})

process_listening = threading.Thread(target=listening_to_main_microservices_serv)
process_listening.start()

listening_loop = discord.ext.tasks.Loop(wait_for_execute, 0, 0, 0, None, True, client.loop)
listening_loop.start()
client.run("ODUxMDQzNTA2NjU5MjYyNDg0.YLyiBw._wW_KwuGd8FUMUIS15dVx3Xs3NA")