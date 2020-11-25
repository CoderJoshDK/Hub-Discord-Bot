import discord, asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get

class Roles(commands.Cog):

    ### On start of code ####
    def __init__(self, bot):
        self.bot = bot
        if len(bot.guilds) > 0:
            self.startup()
    
    def startup(self):
        self.guild = self.bot.guilds[0]
        self.reactionId = 781050277053988884
        self.reactionToRole = {
            "AmongUs" : get(self.guild.roles, id=780967776645808150),
            '👍' : get(self.guild.roles, id=781000687664234536)
        }

    ### Set up the roles####
    @commands.Cog.listener()
    async def on_ready(self):
        self.startup()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        message_id = payload.message_id
        member = payload.member
        if message_id == self.reactionId:
            role = self.reactionToRole[payload.emoji.name]
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        message_id = payload.message_id
        member = get(self.guild.members, id=payload.user_id)
        if message_id == self.reactionId:
            role = self.reactionToRole[payload.emoji.name]
            await member.remove_roles(role)

    @commands.command()
    @has_permissions(administrator=True)
    async def react(self, ctx, emoji):
        messages = await ctx.channel.history(limit=5).flatten()
        message = messages[-1]
        await message.add_reaction(emoji)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(Roles(bot))