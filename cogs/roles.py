import discord
from discord.ext import commands
from discord.utils import get

import emojis
import typing

class ReactionRolesNotSetup(commands.CommandError):
    """Reaction roles are not setup for this guild"""
    pass

def is_setup():
    """
    Check if the guild has reaction roles setup
    """
    async def wrap_func(ctx):
        data = await ctx.bot.config.find(ctx.guild.id)
        if data is None:                    # No guild in config file
            raise ReactionRolesNotSetup
        if data.get("react_message_id") is None:  # No reaction message in data
            raise ReactionRolesNotSetup
        # Data is good so return that it exists
        return True
    # A vaild check setup
    return commands.check(wrap_func)

class Roles(commands.Cog):

    ### On start of code ###
    def __init__(self, bot):
        self.bot = bot
    

    async def rebuild_role_embed(self, guild_id):
        """
        Updates the embed after a role is added/removed
        Params:
         - guild_id (int) : the generated id associated with a given guild
        """
        data = await self.bot.config.find(guild_id)
        channel_id = data["react_channel_id"]
        message_id = data["react_message_id"]

        # Getting the info on where the embed is
        guild = await self.bot.fetch_guild(guild_id)
        channel = await self.bot.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
        
        # All the current reactions to the message
        reactions = message.reactions

        # Start the embed
        embed = discord.Embed(title="Reaction Roles")

        desc = ""
        reaction_roles = await self.bot.reaction_roles.get_all()
        reaction_roles = list(filter(lambda r: r['guild_id'] == guild_id, reaction_roles))
        
        # If a role was removed, get rid of it as a reaction
        emojis = map(lambda r: r["_id"], reaction_roles)
        for reaction in reactions:
            if reaction not in emojis:
                await message.clear_reaction(reaction)
        
        for item in reaction_roles:
            # Get the roles from the reaction item
            role = guild.get_role(item["role"])
            # Add the emoji and ping the role
            desc += f"{item['_id']}: {role.mention}\n"
            
            if (item["_id"] not in reactions):
                # Add the emoji as a reaction if it was added
                await message.add_reaction(item["_id"])
        embed.description = desc
        await message.edit(embed=embed)


    async def get_current_reactions(self, guild_id):
        """
        Return the reactions found in the given guild
        Params:
         - guild_id (int) : the generated id associated with a given guild
        Returns:
         - Data (list) : a list of emojis for the reactions in the guild
        """
        data = await self.bot.reaction_roles.get_all()
        # We only want reactions in guild so use filter
        data = filter(lambda r: r['guild_id'] == guild_id, data)
        # We only want the reaction id and nothing more so use map
        data = map(lambda r: r["_id"], data)
        return list(data)

    @commands.group(
        aliases=['rr'], invoke_without_command=True
    )
    @commands.guild_only()
    async def reactionroles(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), entity="reactionroles")

    @reactionroles.command(name='channel')
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True)
    async def rr_channel(self, ctx, channel: discord.TextChannel = None):
        """Set the channel for the reaction roles"""
        # Set up channel var
        if channel is None:
            await ctx.send("No channel give, I will be using the current one.")
        channel = channel or ctx.channel
        
        # Check if bot can post in channel
        try:
            await channel.send("Testing if I can send messages here", delete_after=0.05)
        except discord.HTTPException:
            await ctx.send("I do not have permissions in that channel. Please give me perms and try again.", delete_after=30)
            return

        # Embed setup
        embed = discord.Embed(
            title = "Reaction Roles"
        )
        desc = ""
        reaction_roles = await self.bot.reaction_roles.get_all()
        # The above gets all reactions roles
        # The filter makes sure that only roles for this id are looked at
        reaction_roles = list(filter(lambda r: r['quild_id'] == ctx.guild.id, reaction_roles))
        for item in reaction_roles:
            role = ctx.guild.get_role(item["role"])
            desc += f"{item['_id']}: {role.mention}\n"
        embed.description = desc

        m = await channel.send(embed=embed)
        for item in reaction_roles:
            await m.add_reaction(item["_id"])

        await self.bot.config.upsert(
            {
                "_id": ctx.guild.id,
                "react_message_id": m.id,
                "react_channel_id": m.channel.id,
                "is_enabled": True,
            }
        )
        await ctx.send("That should be all setup for you", delete_after=30)

    @reactionroles.command(name="toggle")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @is_setup()
    async def rr_toggle(self, ctx):
        """Toggle reaction roles for this guild"""
        data = await self.bot.config.find(ctx.guild.id)
        data["is_enabled"] = not data["is_enabled"]
        await self.bot.config.upsert(data)

        is_enabled = "enabled." if data["is_enabled"] else "disabled."
        await ctx.send(f"The reaction roles have been {is_enabled}")

    @reactionroles.command(
        name="add",
        description="Add a new reaction role",
        usage="<emoji> <role>"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @is_setup()
    async def rr_add(self, ctx, emoji: typing.Union[discord.Emoji, str], *, role: discord.Role):
        """
        Add a new reaction role
        Params:
         - emoji (Emoji & str) : the emoji used for the role
         - role (discord.Role) : the role tied to the emoji
        """
        reactions = await self.get_current_reactions(ctx.guild.id)
        if len(reactions) >= 20:
            await ctx.send("This does not support more than 20 reactio roles per guild")
            return
        
        # If the emoji var is not a discord emoji
        if not isinstance(emoji, discord.Emoji):
            # Get the emoji
            emoji = emojis.get(emoji)
            emoji = emoji.pop()
        # If the emoji is a discord emoji
        elif isinstance(emoji, discord.Emoji):
            # But the bot can not use the emoji just return out
            if not emoji.is_usable():
                await ctx.send("I am unable to use that emoji")
                return

        # Process the data for the data base
        emoji = str(emoji)
        await self.bot.reaction_roles.upsert(
            {
                "_id": emoji, 
                "role": role.id, 
                "guild_id": ctx.guild.id
            }
        )

        await self.rebuild_role_embed(ctx.guild.id)
        await ctx.send("The role and emoji have been added")

    @reactionroles.command(
        name="remove",
        aliases=["delete"],
        description="Remove an existing reaction role",
        usage="<emoji>"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @is_setup()
    async def rr_remove(self, ctx, emoji: typing.Union[discord.Emoji, str]):
        """
        Remove an existing reaction role
        Params:
         - emoji (Emoji & str) : the emoji used for the role
        """
        # If the emoji var is not a discord emoji
        if not isinstance(emoji, discord.Emoji):
            # Get the emoji
            emoji = emojis.get(emoji)
            emoji = emoji.pop()

        # Remove the data from the data base
        emoji = str(emoji)
        await self.bot.reaction_roles.delete(emoji)
        
        await self.rebuild_role_embed(ctx.guild.id)
        await ctx.send("The role has been removed")

    # <---- Listeners ---->

    
    ### To add roles ###
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        data = await self.bot.config.find(payload.guild_id)

        # If the reaction role is not set up, return
        if not payload.guild_id or not data or not data.get("is_enabled"):
            return

        # If the reaction was not on the message that was just reacted, return
        if data["react_message_id"] != payload.message_id:
            return

        # Get the reaction roles
        guild_reaction_roles = await self.get_current_reactions(payload.guild_id)
        # If the emoji isn't one of the reaction roles, return
        if str(payload.emoji) not in guild_reaction_roles:
            return

        guild = await self.bot.fetch_guild(payload.guild_id)

        emoji_data = await self.bot.reaction_roles.find(str(payload.emoji))
        role = guild.get_role(emoji_data["role"])

        member = payload.member
        
        # If the role is not already part of the member, add the role
        if role not in member.roles:
            await member.add_roles(role, reason="Reaction role")    

    
    ### To remove a role ###
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        data = await self.bot.config.find(payload.guild_id)

        # If the reaction role is not set up, return
        if not payload.guild_id or not data or not data.get("is_enabled"):
            return

        # If the reaction was not on the message that was just reacted, return
        if data["react_message_id"] != payload.message_id:
            return

        # Get the reaction roles
        guild_reaction_roles = await self.get_current_reactions(payload.guild_id)
        # If the emoji isn't one of the reaction roles, return
        if str(payload.emoji) not in guild_reaction_roles:
            return

        guild = await self.bot.fetch_guild(payload.guild_id)

        emoji_data = await self.bot.reaction_roles.find(str(payload.emoji))
        role = guild.get_role(emoji_data["role"])

        member = payload.member
        
        # If the role is already part of the member, remove the role
        if role in member.roles:
            await member.remove_roles(role, reason="Reaction role") 
    
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        ### Mute a member that trys to leave and join back ###
        try:
            if self.bot.muted_users[member.id]:
                role = get(member.guild.roles, name="Muted")
                if role:
                    await member.add_roles(role)
        except KeyError:
            pass


    # <---- Commands ---->

    @commands.command(
        description="React to the above msg as the bot",
        usage="<emoji>"
    )
    @commands.has_guild_permissions(administrator=True)
    async def react(self, ctx, emoji):
        await ctx.message.delete()
        
        messages = await ctx.channel.history(limit=2).flatten()
        message = messages[0]
        
        await message.add_reaction(emoji)


def setup(bot):
    bot.add_cog(Roles(bot))