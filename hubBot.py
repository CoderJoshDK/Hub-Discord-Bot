import discord
import os
from discord.ext import commands
from discord.ext.commands import has_permissions

TOKEN = "NzgxMDAyNjMxODYyMDI2MjQw.X73TYQ.js7y7wheQwoIh-ZHPifVkXOxRaI"
intents = discord.Intents.all()
bot = commands.Bot(command_prefix = '!', intents=intents)

######## Start of Bot ################

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online")

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


bot.run(TOKEN)