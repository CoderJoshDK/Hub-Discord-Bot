import discord
import os
from pathlib import Path
from discord.ext import commands
from discord.ext.commands import has_permissions

import logging
import json

cwd = Path(__file__).parents[0]
cwd = str(cwd)
secret_file = json.load(open(cwd+"/Config/secrets.json"))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = '!', intents=intents, case_insensitive=True)
bot.config_token = secret_file['token']
logging.basicConfig(level=logging.INFO)

######## Start of Bot ################

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online")
    await bot.change_presence(activity=discord.Game(f"Hi, I am {bot.user.name}.\nUse ! to interact with me."))

######## Load and unload Cogs ########
'''
To do an event with a cog do 
@commands.Cog.listener()

For commands do
@commands.command()
'''


@bot.command()
@has_permissions(administrator=True)
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f"{extension} is online")

@bot.command()
@has_permissions(administrator=True)
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f"{extension} is offline")

@bot.command()
@has_permissions(administrator=True)
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f"{extension} has been reloaded")

######## Load all cogs when starting up bot ##########

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


bot.run(bot.config_token)