try:
    from discord_bot_microservice_utils.logs_obj import init_a_new_logger
    from discord_bot_microservice_utils.others_objs import pretty_hour_to_timestamp, generate_embed, pretty_number
    from discord_bot_microservice_utils.sql_utils import update_stat, get_stat
    from discord_bot_microservice_utils.sql_utils import command as sql_command
except:
    from logs_obj import init_a_new_logger
    from others_objs import pretty_hour_to_timestamp, generate_embed, pretty_number
    from sql_utils import update_stat, get_stat
    from sql_utils import command as sql_command

from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_actionrow, create_select, create_select_option, wait_for_component

class AwaitedRequest:
    request_id_to_obj = {}

    def __init__(self, request_id: str, args: dict):
        self.args = args
        self.request_id_to_obj[request_id] = self

class DiscordCommands:

    async def send_to_a_microservice(self, ctx, microservice_dest_name, command, args={}, return_req_id=False):
        if not self.microservice.initialized_to_main_microservices_server:
            self.logger.warning("Discord Microservice isn't initialized to microservices server, so a command cannot be sent")
            await ctx.send(":x: Internal Error ||microservice isn't initialized to microservices server||, try again in a few minutes or mention @LupyXev#5816")
            return
        if not hasattr(self.microservice, "sender"):
            self.logger.warning("Discord Microservice has no sender attr, so a command cannot be sent")
            await ctx.send(":x: Internal Error ||microservice has no sender||, try again in a few minutes or mention @LupyXev#5816")
            return
        
        sender = self.microservice.sender
        return sender.send_to_a_microservice(sender.FIRST_REQUEST, microservice_dest_name, command, args, return_req_id=return_req_id)

    def __init__(self, client, microservice):
        self.client = client
        self.slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.
        slash = self.slash
        self.microservice = microservice
        self.logger = init_a_new_logger("Discord Bot Commands - DBM")

        @client.event
        async def on_slash_command(ctx):
            update_stat("total_commands", get_stat("total_commands") + 1)

        guild_ids = [727239318602514526, 842453728154091561] # les Ids des serveurs pour gagner en temps lors de l'ajout de slashs commandes

        @slash.slash(name="ping", description="Show the discord bot latency", guild_ids=guild_ids)
        async def _ping(ctx):
            await ctx.send(f"Pong! ({round(client.latency*1000, 1)}ms)")

        DEFAULT_INTERVALL = "1d"

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
            intervall = pretty_hour_to_timestamp(intervall)
            
            success, verif_code, request_id = await self.send_to_a_microservice(ctx, "hypixel_api_analysis", "get_price_with_search_item_name", {"item_name": item, "intervall": intervall}, return_req_id=True)
            if not success:
                self.logger.warning(f"Req for get_price_with_item_name not successful, code : {verif_code}")
                await ctx.send(":x: Internal error : request not successful | Try again in a few minutes")
            AwaitedRequest(request_id, {"ctx": ctx})
        
        """@slash.slash(name="search-item",
            description="Search a correct item name with a possibly wrong one",
            options=[create_option(name="item_name", description="The item name you watn to search", option_type=3, required=True)],
            guild_ids=guild_ids
        )
        async def _search_item(ctx, item_name):
            success, verif_code, request_id = await self.send_to_a_microservice(ctx, "hypixel_api_analysis", "search_item_name", {"item_name": item_name}, return_req_id=True)
            AwaitedRequest(request_id, {"ctx": ctx})"""
        
        @slash.slash(name="stats",
            description="Show the bot's statistics since 1st publish",
            guild_ids=guild_ids
        )
        async def _stats(ctx):
            embed = generate_embed(
                "📈 Bot's statistics",
                "Statistics since bot's public announcement : 1st June 2021",
                fields=[["Total estimated profit found", f"{pretty_number(get_stat('total_estimated_profit', 'ham_stats'))}", False],
                        ["Total advices amount", f"{pretty_number(get_stat('total_advices', 'ham_stats'))}", True],
                        ["Total advices' price amount", f"{pretty_number(get_stat('total_advices_prices', 'ham_stats'))}", False],
                        ["Total bin auctions scanned", f"{pretty_number(get_stat('total_bin_auctions_scanned', 'ham_stats'))}", True],
                        ["Total bin scanned auctions' price", f"{pretty_number(get_stat('total_bin_auctions_prices', 'ham_stats'))}", False],
                        ["Total commands used", f"{pretty_number(get_stat('total_commands'))}", False]],
            )
            await ctx.send(embed=embed)
        
        @slash.slash(name="donators",
            description="Show the donators & supporters",
            guild_ids=guild_ids
        )
        async def _stats(ctx):
            donators = get_stat("donators", "discord")
            donators_text = "\n".join(donators)
            embed = generate_embed(
                "Donators & Supporters",
                f"Thanks a lot to the project's supporters <:Yep:859453452434538507>\n\n{donators_text}"
            )
            await ctx.send(embed=embed)
        
        @slash.slash(name="dev",
            description="A developer's command (bot administrators only)",
            options=[create_option(name="command", description="The command", option_type=3, required=True)],
            guild_ids=guild_ids
        )
        async def _dev(ctx, command):
            if ctx.author.id == 399978674578784286 or ctx.author.id == 579573266650497035 or ctx.author.id == 409395283617644544:
                #authorised
                await ctx.send(content=":white_check_mark: Authorized")
                if len(command) > 2 and command[:3] == "sql":
                    try:
                        sql_command(command[3:])
                        await ctx.send(content=":white_check_mark: Command done (unverified)")
                    except:
                        await ctx.send(content=":x: An error occured")
                elif len(command) > 11 and command[:11] == "add-donator":
                    donators = get_stat("donators", "discord")
                    donators.append(command[11:])
                    update_stat("donators", donators, "discord")
                    await ctx.send(content=":white_check_mark: Command done (not verified)")
                elif len(command) > 7 and command[:7] == "disable":
                    await ctx.send("Syntax : /dev disable [DURATION_UNTIL_DISABLING_END] [ITEM_NAME]")
                    command_splitted = command.split(" ")
                    duration_since_disabling_end = None
                    try:
                        duration_since_disabling_end = int(pretty_hour_to_timestamp(command_splitted[1]))
                    except:
                        ctx.send(":x: Error with the duration until disabling end")
                        return

                    if len(command_splitted) <= 2:
                        ctx.send(":x: item name needed")
                        return
                    success, verif_code, request_id = await self.send_to_a_microservice(ctx, "hypixel_api_analysis", "search_item_name", {"item_name": " ".join(command_splitted[2:]), "command_to_return_with": "disable"}, return_req_id=True)
                    AwaitedRequest(request_id, {"ctx": ctx, "duration_since_disabling_end": duration_since_disabling_end, "item_name_asked": " ".join(command_splitted[2:])})
                else:
                    await ctx.send(content=":x: Unknow command, commands are : sql, add-donator, disable")
            else:
                await ctx.send(content=":x: Unauthorized")
        
        """@slash.slash(name="config",
            description="Open the server's configuration panel (administrator privilege only)",
            guild_ids=guild_ids
        )
        async def _config(ctx):
            async def verify_admin(author, ctx):
                if author.guild_permissions.administrator is True:
                    return True
                else:
                    await ctx.send(":x: Sorry, administrator privilege needed")
                    return False
            
            if await verify_admin(ctx.author, ctx):
                embed = generate_embed("Configuration panel", "Choose what parameter you want to edit", thumbnail="https://cdn.discordapp.com/attachments/811611272251703357/890307643963506688/setting.webp")
                action_row = create_actionrow(create_select([
                    create_select_option("Alert Channels", "alert_channels"),
                    create_select_option("Alert Roles", "alert_roles")
                ]))
                parameter_choice_message = await ctx.send(embed=embed, components=[action_row])
                option_ctx = await wait_for_component(client, parameter_choice_message, components=action_row)
                
                if await verify_admin(option_ctx.author, ctx):
                    if option_ctx.selected_options[0] == "alert_channels":
                        embed = generate_embed("Edit Alert Channels", "You'll see soon")
                        await ctx.send(embed=embed)

                    elif option_ctx.selected_options[0] == "alert_roles":
                        embed = generate_embed("Edit Alert Roles", "You'll see soon")
                        await ctx.send(embed=embed)

        @slash.slash(name="test",
            description="A test command",
            options=[create_option(name="item_name", description="You'll see", option_type=3, required=True)],
            guild_ids=guild_ids
        )
        async def _test(ctx, item_name):
            
            action_row = create_actionrow(create_select([create_select_option("hey", "idk")]))
            rep = await ctx.send(item_name, components=[action_row])
            await ctx.send("Bye bye I'm going to sleep")"""
            
