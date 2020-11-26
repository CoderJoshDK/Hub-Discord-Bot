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
            if get(self.guild.roles, id=781000687664234536) in member.roles:
                role = self.reactionToRole[payload.emoji.name]
                await member.add_roles(role)
            else:
                await member.send("You must accept the rules before you can gain other roles. To accept them, react to them with the 👍. After accepting the rules, unselect and reselect the roles you want to have")
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
            for role in member.roles:
                if role < get(self.guild.roles, id=780991303806484530) and role != get(self.guild.roles, id=780544594026037298):
                    # All roles below mod and not @everyone is removed
                    await member.remove_roles(role)
            await member.send(f"All of your roles on {self.guild.name} have been removed. Agree to the rules to be able to interact with the server")
            await member.send("After accepting the rules, unselect and reselect the roles you want to have")

    @commands.command()
    @has_permissions(administrator=True)
    async def react(self, ctx, emoji):
        await ctx.message.delete()
        messages = await ctx.channel.history(limit=5).flatten()
        message = messages[0]
        await message.add_reaction(emoji)


def setup(bot):
    bot.add_cog(Roles(bot))