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
        self.red = 0x992d22
        self.purple = 0x9b59b6

    
    ### Set up ###
    @commands.Cog.listener()
    async def on_ready(self):
        self.startup()

    
    @commands.command()
    async def dice(self, ctx):
        """
        Role a random number 1-6
        """
        number = random.randint(1,6)
        
        embed = discord.Embed(
            title="Dice", 
            description=f"You rolled a {number}", 
            color=self.purple
        )

        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        )
        await ctx.send(embed=embed)


    @commands.command()
    async def coin(self, ctx):
        """
        Flip a coin for either heads or tails
        """
        flip = random.randint(0,1)
        
        embed = discord.Embed(
            title="Coin",
            description="Heads" if flip else "Tails",
            color=self.purple
        )

        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        )
        await ctx.send(embed=embed)


    @commands.command()
    async def map(self, ctx):
        """
        Do a poll to see what Among Us map to play
        """
        embed = discord.Embed(
            title="Pick the next map we play on",
            description="What map would you like to play? React to cast your vote!"
        )
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        )
        msg = await ctx.send(embed=embed)
        emojis = [get(ctx.guild.emojis, name="Skeld"), get(ctx.guild.emojis, name="Mira"), get(ctx.guild.emojis, name="Polus")]
        for emoji in emojis:
            await msg.add_reaction(emoji)
    

def setup(bot):
    bot.add_cog(Games(bot))