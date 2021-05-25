import discord, asyncio
from discord.ext import commands
import platform
import DiscordUtils

class Events(commands.Cog):

    ### On start of code ####
    def __init__(self, bot):
        self.bot = bot
        self.tracker = DiscordUtils.InviteTracker(bot)
    

    ### Set up the roles####
    @commands.Cog.listener()
    async def on_ready(self):
        await self.tracker.cache_invites()

   
    ### Deal with diffrent errors ###
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore these errors
        ignored = (commands.CommandNotFound, commands.UserInputError)
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.CommandOnCooldown):
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
        # Implement further custom checks for errors here...
        raise error

    
    ### When someone types a message ###
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return


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