import asyncio
import random

import discord
from discord.ext import commands
from discord.utils import get
from emoji import EMOJI_ALIAS_UNICODE_ENGLISH as EMOJIS

import re
from utils.util import GetMessage, dm_user, sendLog, sendAdmin   # pylint: disable=import-error
from utils.util import Pag          # pylint: disable=import-error

time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?") 
time_dict = {'h': 3600, 's': 1, 'm': 60, 'd': 86400}

### A function for converting a time string into a time in seconds ###
def convert(argument):
    args= argument.lower()
    matches = re.findall(time_regex, args)
    time = 0
    for value, key in matches:
        try:
            time += time_dict[key] * float(value)
        except KeyError:
            raise commands.BadArgument(f"{key} is an invalid key. h|s|m|d are valid")
        except ValueError:
            raise commands.BadArgument(f"{value} is not a number")
    return round(time)


class Stats(commands.Cog):

    ### On start of code ###
    def __init__(self, bot):
        self.bot = bot
        

    async def filtered_commands(self, ctx):
        '''
        Helper command to getting all the commands that a user can run

        Params:
         - ctx (context object) : Used for sending msgs and knowing location
        Returns:
         - filtered (list) : All available commands as the qualified names
        '''
        filtered = []

        for c in self.bot.walk_commands():
            try:
                # Go past hidden and subcommands
                if c.hidden:
                    continue
                elif c.parent:
                    continue
                
                # Only add the command to list if the user can run it
                await c.can_run(ctx)
                filtered.append(c.qualified_name)
            except commands.CommandError:
                # Error trigered by the can_run function if the user can not use the command
                continue
        
        return filtered


    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        '''
        Keep track of what command is used and how often
        '''
        # If the command completed is the logout command, there would be an error if we continue so return to exit
        if ctx.command.qualified_name == 'logout':
            return
        
        # If the command has not been added to the doc, add it
        if await self.bot.command_usage.find(ctx.command.qualified_name) is None:
            await self.bot.command_usage.upsert({"_id" : ctx.command.qualified_name, "usage_count" : 1})
        # Else, the doc is already there so increment the usage by 1
        else: 
            await self.bot.command_usage.increment(ctx.command.qualified_name, 1, "usage_count")

    @commands.command(
        name="commandstats",
        aliases=["usage"],
        description="Show an overall usage for each command"
    )
    @commands.cooldown(1, 5,  commands.BucketType.guild)
    async def command_stats(self, ctx):
        '''
        Show the raw number and percentage of each used command relevent to the user. IE only if they can run that command
        The result will be a Pag class object that can flip through pages
        '''
        # Only get the commands that the user can run. No need to show them the stats on commands they can not use
        useable_commands = await self.filtered_commands(ctx)
        
        data = await self.bot.command_usage.get_all()
        command_map = {item["_id"]: item["usage_count"] for item in data if item["_id"] in useable_commands}

        # Get total commands run since collection
        total_commands_run = sum(command_map.values())

        # Sort by value
        sorted_list = sorted(command_map.items(), key=lambda x: x[1], reverse=True)

        # The pages to display
        pages = []
        cmd_per_page = 10

        # Loop through the commands
        for i in range(0, len(sorted_list), cmd_per_page):
            message = "Command Name: Usage % | Num of command runs\n\n"
            next_commands = sorted_list[i : i + cmd_per_page]

            # All the items in the section of commands
            for item in next_commands:
                use_percentage = item[1] / total_commands_run
                message += f"**{item[0]}**: `{use_percentage: .2%} | Ran {item[1]} times`\n"
            
            # Add the commands and their usage to the page list
            pages.append(message)
        
        await Pag(title="Command Usage Statistics", color=0xC9B4F4, entries=pages, length=1).start(ctx)


    ### Show the number of members in the server ###
    @commands.command(
        description="Display the amount of members in the server"
    )
    async def members(self, ctx):
        embed=discord.Embed(
            title="Members", 
            description=f"There are curently {len(ctx.guild.members)} members in the server", 
            color=0x63d0f7
        )
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    
    ### Report a users for doing something bad ###
    @commands.command(
        description="Send an anonymous report of a user. The staff will be able to see it",
        usage="<member> <reason>"
    )
    async def report(self, ctx, member:discord.Member, *, reason):
        await sendLog(self, ctx, msg=f"<@!{ctx.author.id}> has reported <@!{member.id}> because of {reason}")
        await ctx.message.delete()
        await ctx.author.send("Thank you for reporting. We will look into it and press action if needed", delete_after=10)
    ### If they report wrong ###
    @report.error
    async def report_error(self, ctx, error):
        await ctx.author.send(
            "You have tried to report a user but did something wrong. To use correctly, type `!report @user they did something bad`. We will look into it and get back to you",
            delete_after=15
        )
        await sendLog(self, ctx, msg=f"<@!{ctx.author.id}> has tried to use the report function but failed.\nThey typed: {ctx.message.content}")
        await ctx.message.delete()


    ### Make a poll ###
    @commands.command(
        description="Make a poll to find out what people prefer",
        usage='<question> <options seperated by space>\nPut each part in **""**'
    )
    async def poll(self, ctx, question, *args):
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
                name=f"{emojis[i+1]}",
                value=arg,
                inline=False
            )
        # Send the message
        msg = await ctx.send(embed=embed)
        # Add reactions so people could vote
        for i in range(len(args)):
            await msg.add_reaction(emojis[i+1])

    @commands.command(
        name="giveaway",
        description="Create a full giveaway.",
        usage="Setup in DMs"
    )
    @commands.guild_only()
    async def giveaway(self, ctx):
        ## Change to get info from DMs ##
        await ctx.send("Lets start this giveway, answer the following questions")

        questionList = [
            ['What channel should it be in?', "Mention the channel `<#channel_Id>`"],
            ["How long should this giveaway last?", "`d|h|m|s`"],
            ["What are you giving away?", "I.E. Discord Nitro"],
            ["How many people will win?", "A number: `2`"]
        ]
        answers = {}

        for i, question in enumerate(questionList):
            answer = await GetMessage(self.bot, ctx, question[0], question[1])

            if not answer:
                await ctx.send("You failed to answer, please answer quicker next time.")
                return
            answers[i] = answer

        embed = discord.Embed(
            name="Giveaway content"
        )
        for key, value in answers.items():
            embed.add_field(
                name=f"Question: {questionList[key][0]}", 
                value=f"Answer: `{value}`",
                inline=False
            )
        m = await ctx.send("Are these all valid?", embed=embed)
        await m.add_reaction("☑️")
        await m.add_reaction("🇽")

        try:
            reaction = await self.bot.wait_for(
                "reaction_add",
                timeout=60,
                check = lambda reaction, user: user == ctx.author
                and reaction.message.channel == ctx.channel
            )[0]
        except asyncio.TimeoutError:
            await ctx.send("Confirmation failure. Please try again")
            return
    
        if str(reaction.emoji) not in ["☑️", "🇽"] or str(reaction.emoji) == "🇽":
            await ctx.send("Cancelling giveaway!")
            return
        
        channelId = re.findall(r"[0-9]+", answers[0])[0]
        channel = self.bot.get_channel(int(channelId))

        time = convert(answers[1])

        giveawayEmbed = discord.Embed(
            title="🎉 __**Giveaway**__ 🎉",
            description=answers[2]
        )
        giveawayEmbed.set_footer(text=f"**React 🎉 to enter the giveaway.**\nThis giveway ends {time} second from this message.")
        giveawayMessage = await channel.send(embed=giveawayEmbed)
        await giveawayMessage.add_reaction("🎉")

        await asyncio.sleep(time)

        message = await channel.fetch_message(giveawayMessage.id)
        users = await message.reactions[0].users().flatten()
        users.pop(users.index(ctx.guild.me))

        if len(users) == 0:
            await channel.send("No winner was decided")
            return

        winner = random.choice(users)

        await channel.send(f"**Congrats {winner.mention}!\n**Please contact {ctx.author.mention} about your prize.")
    
    
    ### Show server who left the server ###
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        for channel in member.guild.channels:
            if channel.id == 781581365513945121:
                await channel.send(f'{member.name} has left the server. <@!{member.id}>')

    ### DM a user when they join the guild ###
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await dm_user(member, msg=f"Welcome to {member.guild.name}! Thank you for joining the server. Make sure to read and agree to the rules")

def setup(bot):
    bot.add_cog(Stats(bot))