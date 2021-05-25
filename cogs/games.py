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


    ### Shows the member their randomly sized penis ###
    @commands.command(
        description="Tells you the size of your ego",
        usage="[member]"
    )
    async def penis(self, ctx, member:discord.Member=None):

        if not member:
            member = ctx.author

        # Test to see if a size exists already
        try:
            size = self.bot.penis_size[member.id]["size"]
        except KeyError:
            # If it does not already exist, make the data and add it to file
            size = "=" * random.randint(0,10)
        
            data = {
                '_id': member.id,
                'size': size,
            }
            await self.bot.penisSize.upsert(data)

            self.bot.penis_size[member.id] = data

        # Display the penis
        embed = discord.Embed(color=0xff00ff)
        embed.add_field(
            name=f"{member.display_name}'s Penis Size",
            value=f"8{size}D"
        )
        await ctx.send(embed=embed)    
    
    @commands.command(
        description="Role a random number 1-6. If a number is given, role a number from 1-number",
        usage="[number]"
    )
    async def dice(self, ctx, high=6):
        number = random.randint(1, high)
        
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


    @commands.command(
        description="Flip a coin for either heads or tails"
    )
    async def coin(self, ctx):
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


    @commands.command(
        description="Do a poll to see what Among Us map to play"
    )
    async def map(self, ctx):
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