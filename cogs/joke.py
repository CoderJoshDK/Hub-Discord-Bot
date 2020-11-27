import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get
import random

class Joke(commands.Cog):

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

    @commands.command()
    async def penis(self, ctx, member:discord.Member=None):
        size = "=" * random.randint(0,10)
        embed = discord.Embed(color=0xff00ff)
        if member:
            embed.add_field(
                name=f"{member.name}'s Penis Size",
                value=f"8{size}D"
            )
        else:
            embed.add_field(
                name=f"{ctx.author.name}'s Penis Size",
                value=f"8{size}D"
            )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Joke(bot))