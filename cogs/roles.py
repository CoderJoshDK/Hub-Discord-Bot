import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get

class Roles(commands.Cog):

    ### On start of code ###
    def __init__(self, bot):
        self.bot = bot
        if len(bot.guilds) > 0:
            self.startup()
    
    def startup(self):
        self.guild = self.bot.guilds[0]
        self.reactionId = 781536573421649921 # Roles chat message ID
        self.memberMessageId = 781196607915687986 # Rules message ID
        self.reactionToRole = {
            "AmongUs" : get(self.guild.roles, id=780967776645808150),
            '👍' : get(self.guild.roles, id=781000687664234536)
        }

    ### Set up the roles ###
    @commands.Cog.listener()
    async def on_ready(self):
        self.startup()

    ### To add roles ###
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        message_id = payload.message_id
        member = payload.member
        if message_id == self.reactionId: # Add roles from the role message
            role = self.reactionToRole[payload.emoji.name]
            await member.add_roles(role)
            if get(self.guild.roles, id=781000687664234536) not in member.roles:
                await member.send("Please also accept the rules to see the rest of the server. To accept them, react to them with the 👍.")    
        elif message_id == self.memberMessageId:
            # adding the member role
            role = self.reactionToRole[payload.emoji.name]
            await member.add_roles(role)

    ### To remove a role ###
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        message_id = payload.message_id
        member = get(self.guild.members, id=payload.user_id)
        if message_id == self.reactionId: # Remove a specific roole from the role section
            role = self.reactionToRole[payload.emoji.name]
            await member.remove_roles(role)
        elif message_id == self.memberMessageId: # Dealing with members
            role = self.reactionToRole[payload.emoji.name]
            await member.remove_roles(role)
            await member.send(f"Please agree to the rules of {self.guild.name} to be able to participate in this server. Agree to the rules to be able to interact with the server")

    ### Have bot add reaction to the above message ###
    @commands.command()
    @has_permissions(administrator=True)
    async def react(self, ctx, emoji):
        await ctx.message.delete()
        messages = await ctx.channel.history(limit=5).flatten()
        message = messages[0]
        await message.add_reaction(emoji)


def setup(bot):
    bot.add_cog(Roles(bot))