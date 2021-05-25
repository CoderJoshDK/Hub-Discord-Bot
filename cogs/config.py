import os
import random
import traceback

import asyncio
from utils.util import Pag, dm_user
import discord
from discord.ext import commands

class Config(commands.Cog):

    ### On start of code ###
    def __init__(self, bot):
        self.bot = bot
    
    
    ### Set up the roles ###
    @commands.Cog.listener()
    async def on_ready(self):
        pass

    # <---- Changing the prefix ---->
    @commands.command(
        name="prefix",
        aliases=["changeprefix", "setprefix"],
        description="Change your guilds prefix!",
        usage="[prefix]",
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix(self, ctx, *, prefix=None):
        if not prefix:
            prefix = self.bot.DEFAULTPREFIX
        await self.bot.config.upsert({"_id": ctx.guild.id, "prefix": prefix})
        await ctx.send(
            f"The guild prefix has been set to `{prefix}`. Use `{prefix}prefix [prefix]` to change it again!"
        )

    @commands.command(
        name="deleteprefix", 
        aliases=["dp"], 
        description="Delete your guilds prefix!"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def deleteprefix(self, ctx):
        await self.bot.config.unset({"_id": ctx.guild.id, "prefix": 1})
        await ctx.send("This guilds prefix has been set back to the default")

    @commands.command(
        name="logroom",
        aliases=["log", "lr"],
        description="Set the servers log room where info is sent",
        usage="[channel=current]"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def logroom(self, ctx, channel: discord.channel = None):
        """
        Set the servers log room in the config files
        Params:
         - ctx : commands context
         - channel (discord.channel) : the channel that will be put into the docs
        """
        channel = channel or ctx.channel
        allChannels = ctx.guild.channels
        # Error checking
        if channel not in allChannels:
            await ctx.send("Invalid channel entered. Try sending the channel's id")
            return
        # Setup and let users know
        await self.bot.config.upsert({"_id": ctx.guild.id, "logroom_channel_id": channel.id})
        await channel.send("The log room has been setup", delete_after=30)

    
    @commands.command(
        name="adminroom",
        aliases=["admin", "ar"],
        description="Set the servers admin room where sensitive info is sent",
        usage="[channel=current]"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def adminroom(self, ctx, channel: discord.channel = None):
        """
        Set the servers admin room in the config files
        The info sent to this channel would be things like clear logs. Things that should not be seen or tampered by people
        Params:
         - ctx : commands context
         - channel (discord.channel) : the channel that will be put into the docs
        """
        channel = channel or ctx.channel
        allChannels = ctx.guild.channels
        # Error checking
        if channel not in allChannels:
            await ctx.send("Invalid channel entered. Try using the channel's id\nThe room will be used to send sensative information so make sure only admins can access it")
            return

        await self.bot.config.upsert({"_id": ctx.guild.id, "admin_channel_id": channel.id})

        # No one should be able to interact with the server and only admin overides that
        # If the guild has the channel perms set it might overide this
        await channel.set_permissions(
            ctx.guild.default_role,
            read_messages=False,
            send_messages=False,
            read_message_history=False,
            view_channel=False,
            manage_messages=False,
            reason="Setting up the admin room's perms"
        )

        await channel.send("The admin room has been setup", delete_after=30)



    # <---- Blacklist a user from using the bot ---->
    ### WORK ON// ### Blacklist a user from using bot on guild ###
    @commands.command(
        description="Blacklist someone from being able to use the bot on this server",
        usage="<user>",
        aliases=['bl']
    )
    @commands.has_guild_permissions(administrator=True)
    async def blacklist(self, ctx, user: discord.Member):
        if ctx.message.author.id == user.id:
            await ctx.send("You cannot blacklist yourself!")
            return

        data = await self.bot.config.find(ctx.guild.id)
        if data and "blacklist" in data:
            blacklisted = data["blacklist"].append(user.id)
            await self.bot.config.update_by_id({"_id": ctx.guild.id, "blacklist" : blacklisted})
            self.bot.blacklisted_users[ctx.guild].append(user.id)
        else:
            await data.upsert({"_id" : ctx.guild.id, "blacklist" :  [user]})
            self.bot.blacklisted_users[ctx.guild] = [user.id]
        
        await ctx.send(f"Hey, I have blacklisted {user.name} for you.")

    ### WORK ON// ### Reallow a user to use the bot ###
    @commands.command(
        description="Unblacklist someone from the bot on this server",
        usage="<user>",
        aliases=['ubl']
    )
    @commands.has_guild_permissions(administrator=True)
    async def unblacklist(self, ctx, user: discord.Member):
        data = await self.bot.config.find(ctx.guild.id)
        if data and "blacklist" in data:
            blacklisted = data["blacklist"]
            if user.id in blacklisted: 
                # Only run if the user is blacklisted on this server                
                blacklisted.remove(user.id)
                await self.bot.config.update_by_id({"_id": ctx.guild.id, "blacklist" : blacklisted})
                self.bot.blacklisted_users[ctx.guild.id].remove(user.id)
                
                await ctx.send(f"I have unblacklisted {user.name} for you")
                return
        
        await ctx.send(f"{user.name} was already not blacklisted on this server")

    @commands.command(
        name="logout",
        aliases=["disconnect", "close", "stopbot"],
        description="Log the bot out of discord",
    )
    @commands.is_owner()
    async def logout(self, ctx):
        """
        If the user running the command owns the bot then this will disconnect the bot from discord.
        """
        await self.bot.logout()


    # <---- Cog loading and unloading ---->
    
    @commands.command(
        name='load', 
        description="Load in a cog"
    )
    @commands.is_owner()
    async def load(self, ctx, cog=None):
        if not cog:
            ctx.send("Please specifiy what cog to be loaded")
        else:
            # load the specific cog
            async with ctx.typing():
                embed = discord.Embed(
                    title="Loading the cog!",
                    color=0x808080,
                    timestamp=ctx.message.created_at
                )
                ext = f"{cog.lower()}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                    # if the file does not exist
                    embed.add_field(
                        name=f"Failed to reload: `{ext}`",
                        value="This cog does not exist.",
                        inline=False
                    )

                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.bot.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f"Loaded: `{ext}`",
                            value='\uFEFF',
                            inline=False
                        )
                    except Exception:
                        desired_trace = traceback.format_exc()
                        embed.add_field(
                            name=f"Failed to reload: `{ext}`",
                            value=desired_trace,
                            inline=False
                        )
                await ctx.send(embed=embed)

    
    @commands.command(
        name='unload', 
        description="Unload one of the bots cogs"
    )
    @commands.is_owner()
    async def unload(self, ctx, cog=None):
        if not cog:
            ctx.send("Please specifiy what cog to be")
        else:
            # reload the specific cog
            async with ctx.typing():
                embed = discord.Embed(
                    title="Unloading cog!",
                    color=0x808080,
                    timestamp=ctx.message.created_at
                )
                ext = f"{cog.lower()}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                    # if the file does not exist
                    embed.add_field(
                        name=f"Failed to reload: `{ext}`",
                        value="This cog does not exist.",
                        inline=False
                    )

                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.bot.unload_extension(f"cogs.{ext[:-3]}")
                        self.bot.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f"Reloaded: `{ext}`",
                            value='\uFEFF',
                            inline=False
                        )
                    except Exception:
                        desired_trace = traceback.format_exc()
                        embed.add_field(
                            name=f"Failed to reload: `{ext}`",
                            value=desired_trace,
                            inline=False
                        )
                await ctx.send(embed=embed)

    @commands.command(
        name='reload', 
        description="Reload all/one of the bots cogs"
    )
    @commands.is_owner()
    async def reload(self, ctx, cog=None):
        if not cog:
            # No cog, means we reload all cogs
            async with ctx.typing():
                embed = discord.Embed(
                    title="Reloading all cogs!",
                    color=0x808080,
                    timestamp=ctx.message.created_at
                )
                for ext in os.listdir("./cogs/"):
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.bot.unload_extension(f"cogs.{ext[:-3]}")
                            self.bot.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(
                                name=f"Reloaded: `{ext}`",
                                value='\uFEFF',
                                inline=False
                            )
                        except Exception as e:
                            embed.add_field(
                                name=f"Failed to reload: `{ext}`",
                                value=e,
                                inline=False
                            )
                        await asyncio.sleep(0.5)
                await ctx.send(embed=embed)
        else:
            # reload the specific cog
            async with ctx.typing():
                embed = discord.Embed(
                    title="Reloading all cogs!",
                    color=0x808080,
                    timestamp=ctx.message.created_at
                )
                ext = f"{cog.lower()}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                    # if the file does not exist
                    embed.add_field(
                        name=f"Failed to reload: `{ext}`",
                        value="This cog does not exist.",
                        inline=False
                    )

                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.bot.unload_extension(f"cogs.{ext[:-3]}")
                        self.bot.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f"Reloaded: `{ext}`",
                            value='\uFEFF',
                            inline=False
                        )
                    except Exception:
                        desired_trace = traceback.format_exc()
                        embed.add_field(
                            name=f"Failed to reload: `{ext}`",
                            value=desired_trace,
                            inline=False
                        )
                await ctx.send(embed=embed)

    @commands.command(name="database", aliases=["db", "mongodb"])
    @commands.is_owner()
    async def data(self, ctx, db=None):
        """
        DM The bot owner with the documents stored in the data base
        Params:
         - db (str) : the document that info should be gathered
        """

        # Update with each mongoDB file
        dbs = {
            'config': self.bot.config, 
            'mutes': self.bot.mutes, 
            'penisSize': self.bot.penisSize, 
            'invites': self.bot.invites, 
            'command_usage': self.bot.command_usage, 
            'reaction_roles': self.bot.reaction_roles
        }
        
        if db in dbs:
            db = dbs[db]
            output = ""
            for document in await db.get_all():
                output += document + "\n"

                outputs = [output[i:i + 2000] for i in range(0, len(output), 2000)]
                for out in outputs:
                    await dm_user(self.bot.owner_id, msg=out, self=self)
        else:
            # Display all the names that are available if no name was given or the wrong name was given
            msg = "The available data to look at is" + " / ".join(dbs)
            await dm_user(self.bot.owner_id, msg=msg, self=self)

def setup(bot):
    bot.add_cog(Config(bot))