from utils.util import dm_user
import discord, asyncio
from discord.ext import commands
import platform
import DiscordUtils

class Events(commands.Cog):

    ### On start of code ####
    def __init__(self, bot):
        self.bot = bot
        self.tracker = DiscordUtils.InviteTracker(bot)
    

    @commands.Cog.listener()
    async def on_ready(self):
        await self.tracker.cache_invites()

   
    ### Deal with diffrent errors ###
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore these errors
        ignored = (commands.CommandNotFound,)
        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        # If the user used a command wrong, show them the help page for it
        elif isinstance(error, commands.UserInputError):
            await ctx.invoke(self.bot.get_command("help"), entity=ctx.invoked_with)

        elif isinstance(error, commands.CommandOnCooldown):
            # If the command is currently on cooldown trip this
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if int(h) == 0 and int(m) == 0:
                await ctx.send(f" You must wait {int(s)} seconds to use this command!")
            elif int(h) == 0 and int(m) != 0:
                await ctx.send(
                    f" You must wait {int(m)} minutes and {int(s)} seconds to use this command!"
                )
            else:
                await ctx.send(
                    f" You must wait {int(h)} hours, {int(m)} minutes and {int(s)} seconds to use this command!"
                )
        elif isinstance(error, commands.CheckFailure):
            # If the command has failed a check, trip this
            await ctx.send("You lack permission to use this command.", delete_after=15)
            await ctx.delete(delay=15)
        
        elif isinstance(error, commands.BotMissingPermissions):
            try:
                missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
                if len(missing) > 2:
                    fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
                else:
                    fmt = ' and '.join(missing)
                _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
                await ctx.send(_message)
            except discord.HTTPException:
                pass

        else:
            # Implement further custom checks for errors here...
            await dm_user(self.bot.owner_id, msg=error, ctx=ctx)
            raise error

    
    ### When someone types a message ###
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # If a message was sent to a report room, move that message
        guild = message.guild
        if guild in self.bot.guilds:
            data = await self.bot.config.find(guild.id)
            if data and "reportroom_channel_id" in data:
                if message.channel.id == data["reportroom_channel_id"]:
                    channel = await self.bot.fetch_channel(data["reportroom_channel_id"])
                    await channel.send(f"New report from {message.author.mention}\n{message.content}")
                    await message.delete()


    # <---- Invite Logging ---->

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.tracker.update_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.tracker.update_guild_cache(guild)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.tracker.remove_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.tracker.remove_guild_cache(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        inviter = await self.tracker.fetch_inviter(member)  # inviter is the member who invited
        data = await self.bot.invites.find(inviter.id)
        if data is None:
            data = {
                "_id": inviter.id, 
                "count": 0, 
                "usersInvited": []
            }

        data["count"] += 1
        invitedUser = [member.id, member.joined_at]
        data["usersInvited"].append(invitedUser)
        await self.bot.invites.upsert(data)

def setup(bot):
    bot.add_cog(Events(bot))