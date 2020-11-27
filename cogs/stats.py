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
        embed=discord.Embed(title="Jarvis:", color=0x63d0f7)
        embed.add_field(
            name="Amount of members", 
            value=f"There are curently {len(self.guild.members)} members in the server", 
            inline=True
        )
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        for channel in self.guild.channels:
            if channel.id == 781581365513945121:
                await channel.send(f'{member.name} Has left the server. <@!{member.id}>')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.send(f"Hi, welcome to {self.guild.name}! Please read the rules and agree to them. To agree react with 👍. Some parts of the server you need roles to access. Don't worry, you can get them by reacting to the message under the rules!")

def setup(bot):
    bot.add_cog(Stats(bot))