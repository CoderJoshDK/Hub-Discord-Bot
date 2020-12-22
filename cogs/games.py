import discord
from discord.ext import commands
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

    
    ### Set up ###
    @commands.Cog.listener()
    async def on_ready(self):
        self.startup()

    
    ### Rolls a dice ###
    @commands.command()
    async def dice(self, ctx):
        number = random.randint(1,6)
        
        embed = discord.Embed(color=discord.Color.purple)
        embed.add_field(
                name="Dice",
                value=f"You rolled a {number}"
            )
        await ctx.send(embed=embed)
    ### Error Handling ###
    @dice.error
    async def dice_error(self, ctx, error):
        embed = discord.Embed(color=discord.Color.dark_red)
        embed.add_field(
                name="Dice",
                value=f"How did you mess this up? Just type ONLY !dice"
            )
        await ctx.send(embed=embed)

    
    ### Flips a coin ###
    @commands.command()
    async def coin(self, ctx):
        flip = random.randint(0,1)
        
        embed = discord.Embed(color=discord.Color.purple)
        if flip:
            embed.add_field(
                name="Coin",
                value="Heads"
            )
        else:
            embed.add_field(
                name="Coin",
                value="Tails"
            )
        await ctx.send(embed=embed)
    ### Error Handling ###
    @coin.error
    async def coin_error(self, ctx, error):
        embed = discord.Embed(color=discord.Color.dark_red)
        embed.add_field(
                name="Coin",
                value=f"How did you mess this up? Just type ONLY !coin"
            )
        await ctx.send(embed=embed)
    

def setup(bot):
    bot.add_cog(Games(bot))