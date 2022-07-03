import os
from dotenv import load_dotenv
import hikari
import tanjun
import quoth
import ogs

def build_bot() -> GatewayBot:
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot = hikari.GatewayBot(TOKEN)
    
    make_client(bot)
    
    return bot

def make_client(bot: hikari.GatewayBot) -> tanjun.Client:
    client = (
        tanjun.Client.from_gateway_bot(
            bot,
            mention_prefix=True,
            set_global_commands=GUILD_ID
        )
    ).add_prefix("!")
    
    return client
