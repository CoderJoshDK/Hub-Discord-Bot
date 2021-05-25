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


async def sendLog(self, ctx, msg=None, embed=None, file=None):
    """
    A helper function to send an embed to the guild's log room
    """
    logRoom = await self.bot.config.find(ctx.guild.id)
    if logRoom and "logroom_channel_id" in logRoom:
        channel = await self.bot.fetch_channel(logRoom["logroom_channel_id"])
        try:
            await channel.send(content=msg, embed=embed, file=file)
        except Exception:
            channel = ctx.guild.public_updates_channel
            await channel.send(content=msg, embed=embed, file=file)
            await channel.send("The log room channel set up for this server is not accessible.\nTo fix the log room use command `logroom`")
    else:
        channel = ctx.guild.public_updates_channel
        await channel.send(content=msg, embed=embed, file=file)
        await channel.send("No log room is setup for this server. To setup a log room use command `logroom`\nThe current channel can be used as the log room.")

async def sendAdmin(self, ctx, msg=None, embed=None, file=None):
    """
    A helper function to send an embed/file to the guild's admin room
    """
    adminRoom = await self.bot.config.find(ctx.guild.id)
    if adminRoom and "admin_channel_id" in adminRoom:
        channel = await self.bot.fetch_channel(adminRoom["admin_channel_id"])
        try:
            await channel.send(content=msg, embed=embed, file=file)
        except Exception:
            channel = ctx.guild.public_updates_channel
            await channel.send(content=msg, embed=embed, file=file)
            await channel.send(
                """The admin room channel set up for this server is not accessible.
                To fix the admin room use command `adminroom`"""
            )
    else:
        channel = ctx.guild.public_updates_channel
        await channel.send(content=msg, embed=embed, file=file)
        await channel.send(
            """No admin room is setup for this server. To setup an admin room use command `adminroom`
            The current channel can be used as the admin room just remember that the info sent might be sensative."""
        )

async def dm_user(member, msg=None, embed=None, file=None, ctx=None):
    """
    Send a dm to a user
    """
    if isinstance(member, int):
        if not ctx:
            raise commands.UserInputError("Excpected ctx to be able to fetch the member")
        member = await ctx.guild.fetch_member(member)
    if member is not None:
        channel = member.dm_channel
        if channel is None:
            channel = await member.create_dm()
        await channel.send(content=msg, embed=embed, file=file)
