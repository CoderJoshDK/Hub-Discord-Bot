import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get

class Stats(commands.Cog):

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
    async def members(self, ctx):
        embed=discord.Embed(title="Jarvis:", color=0x00ff40)
        embed.add_field(
            name="Amount of members", 
            value=f"There are curently {len(self.guild.members)} members in the server", 
            inline=True
        )
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Stats(bot))