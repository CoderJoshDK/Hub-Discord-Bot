import discord, asyncio
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

    ### Shows the member their randomly sized penis ###
    @commands.command()
    async def penis(self, ctx, member:discord.Member=None):
        if (ctx.author.id == 471472854546776095 and member == None) or (member and member.id == 471472854546776095):
            size = "=" * random.randint(10, 12)
        elif (ctx.author.id == 472218215083278347 and member == None) or (member and member.id == 472218215083278347):
            size = "E" * random.randint(0,10)
        else:
            size = "=" * random.randint(0,10)

        embed = discord.Embed(color=0xff00ff)
        if member:
            embed.add_field(
                name=f"{member.display_name}'s Penis Size",
                value=f"8{size}D"
            )
        else:
            embed.add_field(
                name=f"{ctx.author.display_name}'s Penis Size",
                value=f"8{size}D"
            )
        await ctx.send(embed=embed)
    
    ### Penis error handaling ###
    @penis.error
    async def penis_error(self, ctx, error):
        embed = discord.Embed(title="Jarvis", color=discord.Color.red)
        embed.add_field(
            name="You used this function wrong",
            value="Either just do !penis for your own size or !penis @user for some other members size"
        )
        await ctx.send(embed=embed)

    ### Randomly messes with people when they are typing ###
    # @commands.Cog.listener()
    # async def on_typing(self, channel, user, when):
    #     if random.randint(0,10000) < 4:
    #         message = await channel.send(f"")
    #         await asyncio.sleep(4)
    #         await message.delete()

def setup(bot):
    bot.add_cog(Joke(bot))