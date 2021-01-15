import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get
from emoji import EMOJI_ALIAS_UNICODE as EMOJIS

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
        """
        Display the amount of members in the server
        """
        embed=discord.Embed(
            title="Members", 
            description=f"There are curently {len(ctx.guild.members)} members in the server", 
            color=0x63d0f7
            )
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    
    ### Report a users for doing something bad ###
    @commands.command()
    async def report(self, ctx, member:discord.Member, *, reason):
        """
        Send an anonymous report of a user. The staff will be able to see it
        """
        await self.reportRoom.send(f"<@!{ctx.author.id}> has reported <@!{member.id}> because of {reason}")
        await ctx.message.delete()
        await ctx.author.send("Thank you for reporting. We will look into it and press action if needed")
    ### If they report wrong ###
    @report.error
    async def report_error(self, ctx, error):
        await ctx.author.send("You have tried to report a user but did something wrong. To use correctly, type `!report @user they did something bad`. We will look into it and get back to you")
        await self.reportRoom.send(f"<@!{ctx.author.id}> has tried to use the report function but failed. They typed: {ctx.message.content}")
        await ctx.message.delete()


    ### Make a poll ###
    @commands.command()
    async def poll(self, ctx, question, *args):
        """
        Find out what people prefer on a topic
        """
        # Dict of number emojis
        emojis = {
            1:EMOJIS[':one:'], 
            2:EMOJIS[':two:'], 
            3:EMOJIS[':three:'], 
            4:EMOJIS[':four:'], 
            5:EMOJIS[':five:'],
            6:EMOJIS[':six:'],
            7:EMOJIS[':seven:'],
            8:EMOJIS[':eight:'],
            9:EMOJIS[':nine:']
        }

        await ctx.message.delete() # Delete the original msg

        embed = discord.Embed(
            title="Poll", 
            description=question, 
            color=0x9b59b6
        )
        embed.set_author(
            name=self.bot.user.name, 
            icon_url=self.bot.user.avatar_url
        )
        
        # Post all the options
        for i, arg in enumerate(args):
            embed.add_field(
                name=f"Option {emojis[i+1]}",
                value=arg,
                inline=False
            )
        # Send the message
        msg = await ctx.send(embed=embed)
        # Add reactions so people could vote
        for i in range(len(args)):
            await msg.add_reaction(emojis[i+1])
        
    
    ### Show server who left the server ###
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        for channel in self.guild.channels:
            if channel.id == 781581365513945121:
                await channel.send(f'{member.name} has left the server. <@!{member.id}>')

    
    ### Message new members so they don't get confused ###
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.send(f"Hi, welcome to {self.guild.name}! Please read the rules and agree to them. Some parts of the server you need roles to access. Don't worry, you can get them by reacting to the message in the get-roles-here channel!")

def setup(bot):
    bot.add_cog(Stats(bot))