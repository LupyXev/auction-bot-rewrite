try:
    from discord_bot_microservice_utils.logs_obj import init_a_new_logger
except:
    from logs_obj import init_a_new_logger

from discord.ext import commands
from discord_slash import SlashCommand 
from discord_slash.utils.manage_commands import create_option

class DiscordCommands:

    async def send_to_a_microservice(self, ctx, microservice_dest_name, command, args={}):
        if not self.microservice.initialized_to_main_microservices_server:
            self.logger.warning("Discord Microservice isn't initialized to microservices server, so a command cannot be sent")
            await ctx.send(":x: Internal Error ||microservice isn't initialized to microservices server||, try again in a few minutes or mention @LupyXev#5816")
            return
        if not hasattr(self.microservice, "sender"):
            self.logger.warning("Discord Microservice has no sender attr, so a command cannot be sent")
            await ctx.send(":x: Internal Error ||microservice has no sender||, try again in a few minutes or mention @LupyXev#5816")
            return
        
        sender = self.microservice.sender
        return sender.send_to_a_microservice(sender.FIRST_REQUEST, microservice_dest_name, command, args)

    def __init__(self, client, microservice):
        self.client = client
        self.slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.
        slash = self.slash
        self.microservice = microservice
        self.logger = init_a_new_logger("Discord Bot Commands - DBM")

        guild_ids = [727239318602514526, 842453728154091561] # les Ids des serveurs pour gagner en temps lors de l'ajout de slashs commandes

        @slash.slash(name="ping", guild_ids=guild_ids)
        async def _ping(ctx): 
            await ctx.send(f"Pong! ({client.latency*1000}ms)")

        DEFAULT_INTERVALL = 2*60*60

        @slash.slash(name="price", 
            description="Show an item's price for a specified intervall",
            options=[
                create_option(name="item",
                    description="The item you want to get the price",
                    option_type=3,
                    required=True
                ),
                create_option(name="intervall",
                    description="The intervall you want for the price",
                    option_type=3,
                    required=False
                )
            ],
            guild_ids=guild_ids
        )
        async def _price(ctx, item, intervall=DEFAULT_INTERVALL):
            good_verif_code, verif_code = await self.send_to_a_microservice(ctx, "hypixel_api_analysis", "test")
            print(verif_code)
            await ctx.send("heyy")