try:
    from discord_bot_microservice_utils.logs_obj import init_a_new_logger
except:
    from logs_obj import init_a_new_logger
from discord import Embed

logger = init_a_new_logger("Others Objs - DBM")

class Alert:
    def __init__(self, absolute_min_to_alert: int, relative_min_to_alert: int, absolute_max_to_alert: int, relative_max_to_alert: int):
        self.absolute_min_to_alert = absolute_min_to_alert
        self.relative_min_to_alert = relative_min_to_alert

        self.absolute_max_to_alert = absolute_max_to_alert
        self.relative_max_to_alert = relative_max_to_alert
    
    def is_this_must_be_alerted(self, absolute_profitability: int, relative_profitability: int):
        if absolute_profitability >= self.absolute_min_to_alert and absolute_profitability <= self.absolute_max_to_alert:
            if relative_profitability >= self.relative_min_to_alert and relative_profitability <= self.relative_max_to_alert:
                return True
        return False

class AlertChannel(Alert):
    def __init__(self, channel_id: int, absolute_min_to_alert: int, relative_min_to_alert: int, absolute_max_to_alert: int, relative_max_to_alert: int):
        super().__init__(absolute_min_to_alert, relative_min_to_alert, absolute_max_to_alert, relative_max_to_alert)
        self.channel_id = channel_id

class AlertRole(Alert):
    def __init__(self, role_id: int, absolute_min_to_alert: int, relative_min_to_alert: int, absolute_max_to_alert: int, relative_max_to_alert: int):
        self.role_id = role_id
        super().__init__(absolute_min_to_alert, relative_min_to_alert, absolute_max_to_alert, relative_max_to_alert)

class Guild:
    guilds_by_id = {}

    @classmethod
    def get_guild_by_id(cls, guild_id):
        if guild_id in cls.guilds_by_id:
            return cls.guilds_by_id[guild_id]
        else:
            #creating a new obj
            logger.info(f"Creating a new Guild obj with guild id : {guild_id}")
            new_obj = Guild(guild_id)
            return new_obj
    
    def __init__(self, guild_id, alert_channels_by_id={}, alert_roles_by_id={}):
        self.guild_id = guild_id
        self.alert_channels_by_id = alert_channels_by_id #id: AlertChannel
        self.alert_roles_by_id = alert_roles_by_id #same as above

        self.guilds_by_id[guild_id] = self

class GlobalDBM:
    run = True
    cur_hypixel_api_run_number = -1

async def generate_embed(message: any, title, title_description, fields=[], footer="🛠️ Made by LupyXev#5816, Strasky#6559 and Saderfing#5924", color=0x1c86ff, thumbnail=None, link="https://discord.com/oauth2/authorize?client_id=811604371073794089&scope=bot&permissions=268954696"):
    embed = Embed(title=title,
        description=title_description,
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

def pretty_number(number, precision=2):
    rounds = [round(number, 1), round(number / 1_000, precision), round(number / 1_000_000, precision)]
    if rounds[0] >= 1_000:  # >999
        if rounds[1] >= 1_000:  # > 999 999
            if rounds[2] >= 1_000:# > 999 999 999
                return str(round(number / 1_000_000_000, precision)) + "B"
            else:
                return str(rounds[2]) + "M"
        else:
            return str(rounds[1]) + "k"
    else:
        return str(rounds[0])