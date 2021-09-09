import discord
from discord.ext import commands
from discord_slash import SlashCommand 
from discord_slash.utils.manage_commands import create_option

client = commands.Bot("a$")

slash = SlashCommand(client, sync_commands=True) # Declares slash commands through the client.

@client.event
async def on_ready():
    print("Ready!")

guild_ids = [727239318602514526, 842453728154091561] # les Ids des serveurs pour gagner en temps lors de l'ajout de slashs commandes

@slash.slash(name="ping", guild_ids=guild_ids)
async def _ping(ctx): 
    await ctx.send(f"Pong! ({client.latency*1000}ms)")

DEFAULT_INTERVALL = 2*60*60

async def _price(ctx, item, intervall=DEFAULT_INTERVALL):
    await ctx.send("priiice")

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
async def slash_price(ctx, item, intervall=DEFAULT_INTERVALL):
    await _price(ctx, item, intervall=DEFAULT_INTERVALL)

@client.command(name="price")
async def pref_price(ctx, item, intervall=DEFAULT_INTERVALL):
    await _price(ctx, item, intervall=DEFAULT_INTERVALL)

@pref_price.error
async def price_error(ctx, error):
    print("errrrrrroooorr")
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(":x: You must send an item name")

client.run("ODUxMDQzNTA2NjU5MjYyNDg0.YLyiBw._wW_KwuGd8FUMUIS15dVx3Xs3NA")