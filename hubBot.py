import discord
import os
from pathlib import Path
from discord.ext import commands
# from discord.ext.commands import has_permissions

import logging

import motor.motor_asyncio
import json
from utils.mongo import Document

from utils.util import Pag, clean_code
import io
import contextlib
import textwrap
from traceback import format_exception


async def get_prefix(bot, message):
    # If dm's
    if not message.guild:
        return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)

    try:
        data = await bot.config.find(message.guild.id)

        # Make sure we have a useable prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)
        return commands.when_mentioned_or(data["prefix"])(bot, message)
    except:
        return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)


######## Start of Bot ################

cwd = Path(__file__).parents[0]
cwd = str(cwd)
secret_file = json.load(open(cwd+"/Config/secrets.json"))

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix =get_prefix, 
    intents=intents, 
    case_insensitive=True,
    help_command=None
)
bot.config_token = secret_file['token']
bot.connection_url = secret_file['mongo']
logging.basicConfig(level=logging.INFO)

bot.version = "1.1.0"
bot.DEFAULTPREFIX = '!'

bot.blacklisted_users = {}
bot.muted_users = {}
bot.penis_size = {}

bot.colors = {
    "WHITE": 0xFFFFFF,
    "AQUA": 0x1ABC9C,
    "GREEN": 0x2ECC71,
    "BLUE": 0x3498DB,
    "PURPLE": 0x9B59B6,
    "LUMINOUS_VIVID_PINK": 0xE91E63,
    "GOLD": 0xF1C40F,
    "ORANGE": 0xE67E22,
    "RED": 0xE74C3C,
    "NAVY": 0x34495E,
    "DARK_AQUA": 0x11806A,
    "DARK_GREEN": 0x1F8B4C,
    "DARK_BLUE": 0x206694,
    "DARK_PURPLE": 0x71368A,
    "DARK_VIVID_PINK": 0xAD1457,
    "DARK_GOLD": 0xC27C0E,
    "DARK_ORANGE": 0xA84300,
    "DARK_RED": 0x992D22,
    "DARK_NAVY": 0x2C3E50,
}
bot.color_list = [c for c in bot.colors.values()]

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online")
    
    await bot.change_presence(activity=discord.Game(f"Hi, I am {bot.user.name}.\nPing me to see my prefix in this server!"))

    print("Initialized Database\n----------------\n")
    print("Configs\n")
    for document in await bot.config.get_all():
        ### Store the information from blacklisted to lower amount of times the docs are read ###
        if 'blacklist' in document:
            bot.blacklisted_users[document["_id"]] = document['blacklist']
        print(document)
    
    print("\n----------------\n")
    print("Muted Users\n")
    for document in await bot.mutes.get_all():
        ### For muted users ###
        bot.muted_users[document["_id"]] = document
        print(document)
    
    print("\n----------------\n")
    print("Command Usage\n")
    usage = await bot.command_usage.get_all()
    for use in usage:
        # Print out the command usage information
        print(use)


    ### For penis size ###
    # Set it in a dict that exists in the bot storage
    sizes = await bot.penisSize.get_all()
    for size in sizes:
        bot.penis_size[size["_id"]] = size['size']

@bot.event
async def on_message(msg):
    if msg.author.id == bot.user.id:
        return
    
    # Blacklisted users are ignored
    if msg.guild and msg.guild.id in bot.blacklisted_users:
        if msg.author in bot.blacklisted_users[msg.guild.id]:
            return 

    #Give prefix when pinged
    if msg.content.startswith(f"<@!{bot.user.id}>") and \
        len(msg.content) == len(f"<@!{bot.user.id}>"
    ):
        data = await bot.config.get_by_id(msg.guild.id)
        if not data or "prefix" not in data:
            prefix = bot.DEFAULTPREFIX
        else:
            prefix = data["prefix"]
        await msg.channel.send(f"My prefix here is `{prefix}`", delete_after=15)
    
    await bot.process_commands(msg)

@bot.command(name="eval", aliases=["exec"])
@commands.is_owner()
async def eval(ctx, *, code):
    """
    Allow the bot owner to run python code in discord
    """
    # Clean up a code block
    code = clean_code(code)
    await ctx.message.delete()

    # Variables to be passed through so the code that is ran
    # Is able to access these variables as their scope
    local_variables={
        "discord" : discord,
        "commands": commands,
        "bot": bot,
        "ctx": ctx,
        "channel": ctx.channel,
        "author": ctx.author,
        "guild": ctx.guild,
        "message": ctx.message
    }

    # Used to get the console output as a string
    stdout = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout):
            # Run the python code
            exec(
                f"async def func():\n{textwrap.indent(code, '    ')}",
                local_variables
            )
            # If the function returns something, get it
            obj = await local_variables["func"]()
            result = f"{stdout.getvalue()}\n-- {obj}\n"
    except Exception as e:
        result = "".join(format_exception(e, e, e.__traceback__))

    pager = Pag(
        timeout=100,
        entries=[result[i:i + 2000] for i in range(0, len(result), 2000)],
        length=1,
        prefix="```py\n",
        suffix="```"
    )

    await pager.start(ctx)


'''
To do an event with a cog do 
@commands.Cog.listener()

For commands do
@commands.command()
'''

######## Load all cogs when starting up bot ##########

if __name__ == "__main__":

    ### Load documents from mongodb ###
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo['Jarvis_Files']
    bot.config = Document(bot.db, 'config')                 # Config
    bot.mutes = Document(bot.db, 'mutes')                   # Muted people
    bot.penisSize = Document(bot.db, 'penisSize')           # Penis Size
    bot.invites = Document(bot.db, 'invites')               # Keep track of who invites who
    bot.command_usage = Document(bot.db, 'command_usage')   # Keep track of how much each command is used
    bot.reaction_roles = Document(bot.db, 'reaction_roles') # Roles that can be acquired by reacting to embed

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith("_"):
            bot.load_extension(f'cogs.{filename[:-3]}')

    bot.run(bot.config_token)