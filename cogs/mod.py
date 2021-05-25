from utils.util import dm_user, sendAdmin, sendLog
import discord, asyncio
from discord.ext import commands, tasks
from discord.utils import get

import os
import traceback
import re
from copy import deepcopy
from dateutil.relativedelta import relativedelta
import datetime


time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?") # pylint: disable=anomalous-backslash-in-string
time_dict = {'h': 3600, 's': 1, 'm': 60, 'd': 86400}

class TimeConverter(commands.Converter):
    ### A class and function for converting a time string into a time in seconds ###
    async def convert(self, ctx, argument):
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

class Mod(commands.Cog):

    ### On start of code ####
    def __init__(self, bot):
        self.bot = bot
        self.mute_task = self.check_current_mutes.start() # pylint: disable=no-member

    def cog_unload(self):
        self.mute_task.cancel()

    
    # <---- Cog tasks ---->
    
    @tasks.loop(minutes=5)
    async def check_current_mutes(self):
        currentTime = datetime.datetime.now()
        mutes = deepcopy(self.bot.muted_users)
        for key, value, in mutes.items():
            if value['muteDuration'] is None:
                continue
            
            unmuteTime = value['mutedAt'] + relativedelta(seconds=value['muteDuration'])

            if currentTime >= unmuteTime:
                guild = self.bot.get_guild(value['guildId'])
                member = guild.get_member(key)

                role = get(guild.roles, name='Muted')
                if role in member.roles:
                    await member.remove_roles(role)
                    try:
                        # Let the guild know that a user was unmuted
                        logRoom = await self.bot.config.find(guild.id)
                        if logRoom and "logroom_channel_id" in logRoom:
                            channel = await self.bot.fetch_channel(logRoom["logroom_channel_id"])
                            try:
                                await channel.send(f"Unmuted : {member.mention}")
                            except Exception:
                                channel = guild.public_updates_channel
                                await channel.send(f"Unmuted : {member.mention}")
                                await channel.send("The log room channel set up for this server is not accessible.\nTo fix the log room use command `logroom`")
                        else:
                            channel = guild.public_updates_channel
                            await channel.send(f"Unmuted : {member.mention}")
                            await channel.send("No log room is setup for this server. To setup a log room use command `logroom`\nThe current channel can be used as the log room.")
                    except:
                        pass

                await self.bot.mutes.delete(member.id)
                try:
                    self.bot.muted_users.pop(member.id)
                except KeyError:
                    pass
                    

    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.bot.wait_until_ready()


    ### Mute someone ###
    @commands.command(
        name="mute",
        description="Mute users on server and prevent them from typing or joining VC",
        usage="<user> [time] [reason]"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(mute_members=True)
    async def mute(self, ctx, member : discord.Member, time: TimeConverter=None, *, reason=None):
        
        role = get(ctx.guild.roles, name="Muted")
        pfp = member.avatar_url
        try: 
            # creates muted role 
            if not role:
                role = await ctx.guild.create_role(name="Muted", reason="To use for muting")
            # Go through every channel and set up permissions
            # Do this on every call to make sure that even if the channels were edited, the role still works
            for channel in ctx.guild.channels: 
                # removes permission to view and send in the channels 
                await channel.set_permissions(
                    role, 
                    send_messages=False,                        
                    read_message_history=False,
                    read_messages=False
                )
        except discord.Forbidden:
            return await ctx.send("I do not have permissions to set up a muted role\nMake sure to give me manage roles permission")
    
        # Test if the user is already muted. If so there is no need to do anything more
        try:
            if self.bot.muted_users[member.id] and role in member.roles:
                await ctx.send(f"This user is already muted")
                return
        except KeyError:
            pass
        
        # The information that will be stored in the file
        data = {
            '_id': member.id,
            'mutedAt': datetime.datetime.now(),
            'muteDuration': time or None,
            'mutedBy': ctx.author.id,
            'guildId': ctx.guild.id
        }
        await self.bot.mutes.upsert(data)

        self.bot.muted_users[member.id] = data

        await member.add_roles(role, reason=reason)
        if member.voice:
            await member.edit(voice_channel=None)     # Take them out of voice chat if they are in one 

        if not time:
            await ctx.send(f"Muted {member.mention}")
        else:
            minutes, seconds = divmod(time, 60)
            hours, minutes = divmod(minutes, 60)
            if int(hours):
                embed=discord.Embed(
                    title=f"Muted by {ctx.author.display_name}",
                    description=f"Muted {member.mention} for {hours} hours, {minutes} minutes and {seconds} seconds\n{reason}",
                    color=0x00ff40
                )
            elif int(minutes):
                embed=discord.Embed(
                    title=f"Muted by {ctx.author.display_name}",
                    description=f"Muted {member.mention} for {minutes} minutes and {seconds} seconds\n{reason}",
                    color=0x00ff40
                )
            elif int(seconds):
                embed=discord.Embed(
                    title=f"Muted by {ctx.author.display_name}",
                    description=f"Muted {member.mention} for {seconds} seconds\n{reason}",
                    color=0x00ff40
                )
            
            embed.set_author(
                name=member.display_name,
                icon_url=pfp
            )
            await ctx.send(embed=embed)
            await sendLog(self, ctx, embed=embed)
        
        if time and time < 300: # Do the timer here if the time left is small
            await asyncio.sleep(time)

            if role in member.roles:
                await member.remove_roles(role)

            await self.bot.mutes.delete(member.id)
            try:
                self.bot.muted_users.pop(member.id)
            except KeyError:
                pass
                
            # Unmute embed
            embed=discord.Embed(
                title="Unmuted", 
                description=f"{member.mention} has been unmuted.",
                color=0x00ff40
            )
            embed.set_author(
                name=member.display_name,
                icon_url=pfp
            )
            await ctx.send(embed=embed)
            await sendLog(self, ctx, embed=embed)

    ### When something goes wrong with the mute function ###
    @mute.error
    async def mute_error(self, ctx, error):
        embed=discord.Embed(
            title="Mute Error", 
            color=0xf22929,
            description=f"Something went wrong. It has been logged and will be looked into"
        )
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        )
        await ctx.send(embed=embed)
        
        # Log the error #
        embed = discord.Embed(
            color=0xe74c3c, 
            title="Mute Error",
            description=f"An error on the mute command\n{error}"
        ) 
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        )
        await dm_user(self.bot.owner.id, embed=embed, ctx=ctx)
    
    ### Unmute a member if they served long enough ###
    @commands.command(
        name="unmute",
        description="Umute a user. They can interact with the server again",
        usage="<user>"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(mute_members=True)
    async def unmute(self, ctx, member:discord.Member):
        role = get(ctx.guild.roles, name="Muted")
        pfp = member.avatar_url

        await self.bot.mutes.delete(member.id)
        try:
            self.bot.muted_users.pop(member.id)
        except KeyError:
            pass
        
        if role not in member.roles:
            embed = discord.Embed(
                title="Unmute",
                description=f"This member is not muted",
                color=0xe74c3c
            )
            embed.set_author(
                name=self.bot.user.name,
                icon_url=self.bot.user.avatar_url
            )
            await ctx.send(embed=embed)
            return
        
        await member.remove_roles(role)
        embed = discord.Embed(
            title="Unmute",
            description=f"{member.mention} has been unmuted by {ctx.author.mention}",
            color=0x1f8b4c
        ) 
        embed.set_author(
            name=member.display_name,
            icon_url=pfp
        )
        await ctx.send(embed=embed)
        await sendLog(self, ctx, embed=embed)
        
    
    ### Clear a channels messages by some amount ###
    @commands.command(
        description="Delete the amount specified messeges on channel",
        usage="[amount]"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int=10):
        filename = f"{ctx.channel.name}_clear.txt" # Make text file
        with open(filename, "w", encoding="UTF-8") as file:
            file.write(f"{ctx.author} cleared {amount} messages of {ctx.channel.name} in {ctx.channel.category.name}\n\n") # Log action
            async for msg in ctx.channel.history(limit=amount): # Go through channels messages
                try:
                    file.write(f"{msg.created_at} - {msg.author.display_name}: {msg.clean_content}\n") # Log the deleted text
                except:
                    file.write(f"{msg.created_at} - {msg.author.display_name}: Message could not be displayed\n")
        await ctx.channel.purge(limit=amount) # Delete messages
        await sendAdmin(self, ctx, file=discord.File(filename)) # Post the delete log
    @clear.error
    async def clear_error(self, ctx, error):
        embed = discord.Embed(
            color=0xe74c3c, 
            title="Clear Error",
            description=f"To use the clear command, type !clear [amount]\nThere was an error somewhere"
            ) 
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        )
        await ctx.send(embed=embed) # Post the embed
        embed = discord.Embed(
            color=0xe74c3c, 
            title="Clear Error",
            description=f"An error on the clear command\n{error}"
            ) 
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        )
        await sendAdmin(self, ctx, embed=embed)
    
    
    ### Clear a channel's messages by some amount for some user ###
    @commands.command(
        description="Delete Messeges of a specific user",
        usage="<member> [amount]"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def purge(self, ctx, member:discord.Member, amount=10):
        filename = f"{member.display_name}_purge.txt" # Make a text file

        def is_m(m): # Checks if messages author is the member being purged
            return m.author == member and m.author != self.bot.user

        with open(filename, "w", encoding="UTF-8") as file:
            file.write(f"{ctx.author} cleared {amount} messages of {member.display_name} in {ctx.channel.name}\n\n") # Log action
            
            for channel in ctx.guild.text_channels: # Go through all text channels of guild
                file.write(f"\nMessages from {channel.name} in {channel.category.name}:\n") # Break up the logs by channel
                async for msg in channel.history(limit=amount): # Go through channel's messages
                    if msg.author == member:
                        try:
                            file.write(f"{msg.created_at} - {msg.author.display_name}: {msg.clean_content}\n") # Log the deleted text
                        except:
                            file.write(f"{msg.created_at} - {msg.author.display_name}: Message could not be displayed\n")
                await channel.purge(limit=amount, check=is_m) # Delete messages of member
        await sendAdmin(self, ctx, file=discord.File(filename)) # Post the delete log
    @purge.error
    async def purge_error(self, ctx, error):
        embed = discord.Embed(
            color=0xe74c3c, 
            title="Purge Error",
            description=f"To use the purge command, type !purge <member> [amount]\nThere was an error somewhere. It has been logged and will be looked into"
        ) 
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        )
        await ctx.send(embed=embed) # Post the embed
        
        embed = discord.Embed(
            color=0xe74c3c, 
            title="Error",
            description=f"An error on the purge command\n{error}"
        ) 
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        )
        await dm_user(self.bot.owner.id, embed=embed, ctx=ctx) # Log what the error was
 
def setup(bot):
    bot.add_cog(Mod(bot))