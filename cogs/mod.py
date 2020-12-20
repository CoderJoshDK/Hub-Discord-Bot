import discord, asyncio
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.utils import get

class Mod(commands.Cog):

    ### On start of code ####
    def __init__(self, bot):
        self.bot = bot
        if len(bot.guilds) > 0:
            self.startup()
    
    def startup(self):
        self.guild = self.bot.guilds[0]
        self.mutedMembers = []
        self.mod = get(self.guild.roles, name="Mod")
        self.admin = get(self.guild.roles, name="Admin")
        self.logRoom = get(self.guild.channels, id=780993363146178580)
        self.hiddenLogRoom = get(self.guild.channels, id=789877007638986772)

    ### Set up the roles####
    @commands.Cog.listener()
    async def on_ready(self):
        self.startup()
        muted_role = get(self.guild.roles, name="Muted")
        member_role = get(self.guild.roles, name="Member")
        for member in self.guild.members:
            if muted_role in member.roles:
                await member.remove_roles(muted_role, reason="Bot reloaded")
                await member.add_roles(member_role)

    ### Make sure only admin or mods can use this cog ###
    async def cog_check(self, ctx):
        return self.mod in ctx.author.roles or self.admin in ctx.author.roles

    ### When someon types a message ###
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        ### If a muted member can still somehow type, the thing they type will be deleted ###
        if message.author in self.mutedMembers:
            await message.delete()

    ### Mute someone ###
    @commands.command()
    async def mute(self, ctx, member : discord.Member, time="5m", *, reason="spam"):    
        # Set time to right seconds
        seconds = None
        if time.endswith("m"):
            seconds = int(time[:-1]) * 60
        elif time.endswith("s"):
            seconds = int(time[:-1])
        elif time.endswith("h"):
            seconds = int(time[:-1]) * 60 * 60
        elif time.endswith("d"):
            seconds = int(time[:-1]) * 60 * 60 * 24
        
        if seconds: # Mute someone and let people know it is happening
            # Mute embed
            embed=discord.Embed(title="Jarvis:", color=0x00ff40)
            embed.add_field(
                name="Mute", 
                value=f"{member.display_name} has been muted for {time} because of {reason} by {ctx.author.display_name}", 
                inline=True
            )
            await ctx.send(embed=embed)
            
            ### Mute them and then unmute them after time ###
            muted_role = get(ctx.guild.roles, name="Muted")
            member_role = get(ctx.guild.roles, name="Member")

            await member.add_roles(muted_role, reason=reason) # Make them muted
            self.mutedMembers.append(member) # Put them on the muted list
            try:
                await member.move_to(None) # Take them out of voice chat if they are in one
            except:
                pass
            await member.remove_roles(member_role) # Member roles can type so get rid of it
            await self.logRoom.send(f"<@!{ctx.author.id}> muted <@!{member.id}> because of {reason} for {time}") # Log the mute

            await asyncio.sleep(seconds) # Wait for time to pass

            self.mutedMembers.remove(member) # Take them off the muted list

            if self.guild.get_member(member.id) != None: # Can only do these things if member is still in guild or you get error
                await member.remove_roles(muted_role, reason="Time is up") # Get rid of muted role
                await member.add_roles(member_role) # Make them a member again
            
            # Unmute embed
            embed=discord.Embed(title="Jarvis:", color=0x00ff40)
            embed.add_field(
                name="Unmuted", 
                value=f"{member.display_name} has been unmuted. {time} has past", 
                inline=True
            )
            await ctx.send(embed=embed)

        else: # Invalid time
            embed=discord.Embed(title="Jarvis:", color=0xf22929)
            embed.add_field(
                name="Mute", 
                value="Enter a valid amount of time.", 
                inline=False
                )
            embed.add_field(
                name="Example", 
                value="30s, 10m, 2d, 1h", 
                inline=True)
            await ctx.send(embed=embed)
    
    ### When something goes wrong with the mute function ###
    @mute.error
    async def mute_error(self, ctx, error):
        embed=discord.Embed(title="Jarvis:", color=0xf22929)
        embed.add_field(
            name="Mute", 
            value="You did something wrong", 
            inline=False
            )
        embed.add_field(
            name="Use", 
            value="!mute [@user] [time] [reason] (you must be a mod or above to use this function)", 
            inline=False
            )
        await ctx.send(embed=embed)

    ### Unmute a member if they served long enough ###
    @commands.command()
    async def unmute(self, ctx, member:discord.Member):
        muted_role = get(ctx.guild.roles, name="Muted")
        member_role = get(ctx.guild.roles, name="Member")

        await member.remove_roles(muted_role, reason="They have been unmuted")
        await member.add_roles(member_role)
        
        embed = discord.Embed(color=discord.Color.dark_green)
        embed.add_field(
            name="Unmute",
            value=f"{member.display_name} has been unmuted"
        )

        await ctx.send(embed=embed)
        
    ### Clear a channels messages by some amount ###
    @commands.command()
    async def clear(self, ctx, amount=10):
        filename = f"{ctx.channel.name}_clear.txt" # Make text file
        with open(filename, "w") as file:
            file.write(f"{ctx.author} cleared {amount} messages in {ctx.channel.name}\n") # Log action
            async for msg in ctx.channel.history(limit=amount): # Go through channels messages
                file.write(f"{msg.created_at} - {msg.author.display_name}: {msg.clean_content}\n") # Log the deleted text
        await ctx.channel.purge(limit=amount) # Delete messages
        await self.hiddenLogRoom.send(file=discord.File(filename)) # Post the delete log
    
    ### Clear a channel's messages by some amount for some user ###
    @commands.command()
    async def purge(self, ctx, member:discord.Member, amount=10):
        filename = f"{member.display_name}_purge.txt" # Make a text file

        def is_m(m): # Checks if messages author is the member being purged
            return m.author == member and m.author != self.bot.user

        with open(filename, "w") as file:
            file.write(f"{ctx.author} cleared {amount} messages of {member.display_name} in {ctx.channel.name}\n\n\n") # Log action
            
            for channel in self.guild.channels: # Go through all channels of guild
                file.write(f"Messages from {channel.name}:\n\n") # Break up the logs by channel
                async for msg in channel.history(limit=amount): # Go through channel's messages
                    if msg.author == member:
                        file.write(f"{msg.created_at} - {msg.author.display_name}: {msg.clean_content}\n") # Log the deleted text
                await channel.purge(limit=amount, check=is_m) # Delete messages of member
        await self.hiddenLogRoom.send(file=discord.File(filename)) # Post the delete log

def setup(bot):
    bot.add_cog(Mod(bot))