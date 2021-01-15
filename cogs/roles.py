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
        self.reactionToRole = {
            "AmongUs" : get(self.guild.roles, name="Among Us"),
            "Groovy" : get(self.guild.roles, name="DJ"),
            "Minecraft" : get(self.guild.roles, name="Minecraft"),
            "ThinkPad" : get(self.guild.roles, name="Haker Man"),
            "Cards" : get(self.guild.roles, name="Cards")
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

    
    ### To remove a role ###
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        message_id = payload.message_id
        member = get(self.guild.members, id=payload.user_id)
        
        if message_id == self.reactionId: # Remove a specific roole from the role section
            role = self.reactionToRole[payload.emoji.name]
            await member.remove_roles(role)
    
    
    @commands.command()
    @has_permissions(administrator=True)
    async def react(self, ctx, emoji):
        """
        React to the above msg as the bot
        """
        await ctx.message.delete()
        
        messages = await ctx.channel.history(limit=2).flatten()
        message = messages[0]
        
        await message.add_reaction(emoji)


def setup(bot):
    bot.add_cog(Roles(bot))