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
        self.reportRoom = get(self.guild.channels, id=782084427022991451)

    ### Set up the roles ###
    @commands.Cog.listener()
    async def on_ready(self):
        self.startup()

    ### Show the number of members in the server ###
    @commands.command()
    async def members(self, ctx):
        embed=discord.Embed(title="Jarvis:", color=0x63d0f7)
        embed.add_field(
            name="Amount of members", 
            value=f"There are curently {len(self.guild.members)} members in the server", 
            inline=True
        )
        await ctx.send(embed=embed)

    ### Report a users for doing something bad ###
    @commands.command()
    async def report(self, ctx, member:discord.Member, *, reason):
        await self.reportRoom.send(f"<@!{ctx.author.id}> has reported <@!{member.id}> because of {reason}")
        await ctx.author.send("Thank you for reporting. We will look into it and press action if needed")
        await ctx.message.delete()
    
    ### If they report wrong ###
    @report.error
    async def report_error(self, ctx, error):
        await ctx.author.send("You have tried to report a user but did something wrong. To use correctly, type `!report @user they did something bad`. We will look into it and get back to you")
        await self.reportRoom.send(f"<@!{ctx.author.id}> has tried to use the report function but failed. They typed: {ctx.message.content}")
        await ctx.message.delete()
    
    ### Show server who left the server ###
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        for channel in self.guild.channels:
            if channel.id == 781581365513945121:
                await channel.send(f'{member.name} has left the server. <@!{member.id}>')

    ### Message new members so they don't get conffused ###
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.send(f"Hi, welcome to {self.guild.name}! Please read the rules and agree to them. To agree react with 👍. Some parts of the server you need roles to access. Don't worry, you can get them by reacting to the message under the rules!")

def setup(bot):
    bot.add_cog(Stats(bot))