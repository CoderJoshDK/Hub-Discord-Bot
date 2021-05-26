import asyncio

import discord
from discord.ext import commands
from discord.ext.buttons import Paginator

class Pag(Paginator):
    '''
    A class to overwrite functions
    '''
    async def teardown(self):
        '''
        Clear all the reactions to keep it clear
        Default does not do this
        '''
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass


async def GetMessage(
    bot, ctx, contentOne="Default Message", contentTwo="\uFEFF", timeout=100
):
    """
    This function sends an embed containing the params and then waits for a message to return
    Params:
     - bot (commands.Bot object) :
     - ctx (context object) : Used for sending msgs and knowing location
     - Optional Params:
        - contentOne (string) : Embed title
        - contentTwo (string) : Embed description
        - timeout (int) : Timeout for wait_for
    Returns:
     - msg.content (string) : If a message is detected, the content will be returned
    or
     - False (bool) : If a timeout occurs
    """
    embed = discord.Embed(
        title=f"{contentOne}",
        description=f"{contentTwo}",
    )
    sent = await ctx.send(embed=embed) # pylint: disable=unused-variable
    try:
        msg = await bot.wait_for(
            "message",
            timeout=timeout,
            check=lambda message: message.author == ctx.author
            and message.channel == ctx.channel,
        )
        if msg:
            return msg.content
    except asyncio.TimeoutError:
        return False

def clean_code(content):
    """
    Clean up some code for Eval. 
    If the code is in a code block, get rid of it
    """
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content


async def sendLog(self, ctx, msg: str=None, embed:discord.Embed=None, file:discord.File=None):
    """
    A helper function to send a message to the guild's log room
    Params :
     - self : Cog class self
     - ctx : context of the called command
     - Optional Params :
        - msg (str) : a string for the message to be sent
        - embed (discord.Embed) : the embed to be sent
        - file (discord.File) : the file to be sent
    """
    channels = []
    data = await self.bot.config.find(ctx.guild.id)
    if data:
        channels += getChannels(self, data, ["logroom_channel_id"])
    channels += ctx.guild.public_updates_channel
    await sendToImportantChannel(ctx, channels, msg=msg, embed=embed, file=file, error="Use `logroom` to set up a log room for me to send my information to")

async def sendAdmin(self, ctx, msg=None, embed=None, file=None):
    """
    A helper function to send a message to the guild's admin room
    Params :
     - self : Cog class self
     - ctx : context of the called command
     - Optional Params :
        - msg (str) : a string for the message to be sent
        - embed (discord.Embed) : the embed to be sent
        - file (discord.File) : the file to be sent
    """
    channels = []
    data = await self.bot.config.find(ctx.guild.id)
    if data:
        channels += getChannels(self, data, ["admin_channel_id", "logroom_channel_id"])
    channels += ctx.guild.public_updates_channel
    await sendToImportantChannel(ctx, channels, msg=msg, embed=embed, file=file, error="Use `admin` to set up an admin room for me to send my information to")


async def getChannels(self, data, searches):
    """
    Get a list of channels from the data base and look at the searches
    Params:
     - self : the Cog that calls this. Needed for the bot
     - data : the data base file to look through
     - searches (list) : a list of strings of the data entry to look at
    Returns:
     - channels (list) : a list of the channels that exist in the data base 
    """
    channels = []
    for search in searches:
        if data and search in data:
            try:
                channel = await self.bot.fetch_channel(data[search])
                channels.append(channel)
            except Exception:
                pass
    return channels

    
async def sendToImportantChannel(ctx, channels: list, msg=None, embed=None, file=None, error="I do not have permision to send messages in the expected channel"):
    """
    Try to send a message to the first availabe channel in a given list
    Params:
     - ctx : context of where a command is called
     - channels (list) : a list of discord.channel where each channel will be gone through one at a time and checked
     - Optional Params :
        - msg (str) : the words to be sent in a message
        - embed (discord.Embed) : embed for the bot to send
        - file (discord.File) : a file to be sent
        - error (str) : a message to display if the sent message was not in the expected original location
    Returns:
     - channel (discord.channel) : the channel that finally sent the message or None if none was sent
    """
    # Get rid of all None type from the list
    channels = [i for i in channels if i]

    # Go through each channel and try to send a message
    for channel in channels:
        # Get the bots permissions on the current channel
        perms = channel.permissions_for(ctx.guild.me)
        if(perms.send_messages):
            await channel.send(content=msg, embed=embed, file=file)
            # If the channel being sent to is not the original channel, send error message
            if channel is not channels[0]:
                await channel.send(error)
            # Once one message is sent, we are done. Return out of function
            return channel
    
    # Let the caller of the command know that there was a problem
    try:
        await ctx.send(f"I do not have permision to send messages in the expected channel.\n{error}")
        return ctx.channel
    except Exception:
        return None

        

async def dm_user(member, msg=None, embed=None, file=None, ctx=None):
    """
    Send a dm to a user
    Params:
     - member (discord.Member)
     - msg (str)
     - embed (discord.Embed)
     - file (discord.File)
     - ctx
    """
    # If the 'member' is just an int, get them as a member object
    if isinstance(member, int):
        if not ctx:
            raise commands.UserInputError("Excpected ctx to be able to fetch the member")
        member = await ctx.guild.fetch_member(member)
    if member is not None:
        channel = member.dm_channel
        if channel is None:
            channel = await member.create_dm()
        await channel.send(content=msg, embed=embed, file=file)
