import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get
import random

class Games(commands.Cog):

    ### On start of code ###
    def __init__(self, bot):
        self.bot = bot
        if len(bot.guilds) > 0:
            self.startup()
    
    def startup(self):
        self.guild = self.bot.guilds[0]

    ### Set up the roles ###
    @commands.Cog.listener()
    async def on_ready(self):
        self.startup()

    ### Rolls a dice ###
    @commands.command()
    async def dice(self, ctx):
        number = random.randint(1,6)
        await ctx.send(f"You rolled a {number}")
    
    
    

def setup(bot):
    bot.add_cog(Games(bot))