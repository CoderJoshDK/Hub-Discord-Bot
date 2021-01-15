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
        return ctx.author.top_role >= self.mod

   
    ### Deal with diffrent errors ###
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            pass
        ignored = (commands.CommandNotFound, commands.UserInputError)
        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.CheckFailure):
            await ctx.channel.purge(limit=1)
            await ctx.send("You do not have permision to do that")
            return

    
    ### When someon types a message ###
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        ### If a muted member can still somehow type, the thing they type will be deleted ###
        if message.author in self.mutedMembers:
            await message.delete()


    ### Mute someone ###
    @commands.command()
    async def mute(self, ctx, member : discord.Member, time="5m", *, reason="spam"):
        """
        Make it so that a user can not interact with the server. Talk or type
        """    
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
            embed=discord.Embed(
                title="Muted",
                description=f"{member.display_name} has been muted for {time} because of {reason} by {ctx.author.display_name}",
                color=0x00ff40
            )
            embed.set_author(
                name=self.bot.user.name,
                icon_url=self.bot.user.avatar_url
            )
            await ctx.send(embed=embed)
            
            ### Mute them and then unmute them after time ###
            muted_role = get(ctx.guild.roles, name="Muted")

            await member.add_roles(muted_role, reason=reason) # Make them muted
            self.mutedMembers.append(member) # Put them on the muted list

            try:
                await member.edit(mute=True, deafen=True) # Mute and deafen them
                if member.voice:
                    await member.edit(voice_channel=None)     # Take them out of voice chat if they are in one 
            except:
                pass
            await self.logRoom.send(f"<@!{ctx.author.id}> muted <@!{member.id}> because of {reason} for {time}") # Log the mute

            await asyncio.sleep(seconds) # Wait for time to pass

            self.mutedMembers.remove(member) # Take them off the muted list
            await member.edit(mute=False, deafen=False) # Un server mute and deafen

            if self.guild.get_member(member.id) != None: # Can only do these things if member is still in guild or you get error
                await member.remove_roles(muted_role, reason="Time is up") # Get rid of muted role
            
            # Unmute embed
            embed=discord.Embed(
                title="Unmuted", 
                description=f"{member.display_name} has been unmuted. {time} has past",
                color=0x00ff40
            )
            embed.set_author(
                name=self.bot.user.name,
                icon_url=self.bot.user.avatar_url
            )
            await ctx.send(embed=embed)

        else: # Invalid time
            embed=discord.Embed(
                title="Error on mute", 
                description="Enter a valid amount of time.",
                color=0xf22929
            )
            embed.add_field(
                name="Example", 
                value="30s, 10m, 2d, 1h", 
                inline=True
            )
            embed.set_author(
                name=self.bot.user.name,
                icon_url=self.bot.user.avatar_url
            )
            await ctx.send(embed=embed)
    ### When something goes wrong with the mute function ###
    @mute.error
    async def mute_error(self, ctx, error):
        embed=discord.Embed(title="Mute", color=0xf22929)
        embed.add_field(
            name="Mute", 
            value="You did something wrong", 
            inline=False
        )
        embed.add_field(
            name="Usage", 
            value="!mute [@user] [time] [reason] (you must be a mod or above to use this function)", 
            inline=False
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
        await self.hiddenLogRoom.send(embed=embed)

    
    ### Unmute a member if they served long enough ###
    @commands.command()
    async def unmute(self, ctx, member:discord.Member):
        """
        Unmute a user. They can interact with the server again
        """
        muted_role = get(ctx.guild.roles, name="Muted")

        await member.remove_roles(muted_role, reason="They have been unmuted")     
        try:
            self.mutedMembers.remove(member) # Removes them from the muted list
            await member.edit(mute=False, deafen=False) # Un server mute and deafen
        except: # If they are not in the muted list, let them know
            embed = discord.Embed(
                title="Unmute",
                description=f"{member.display_name} was not muted",
                color=0xe74c3c
            ) 
        else: # If they are in the muted list say it has finished
            embed = discord.Embed(
                title="Unmute",
                description=f"{member.display_name} has been unmuted",
                color=0x1f8b4c
            ) 
            embed.add_field(
                name="Unmute",
                value=f"{member.display_name} has been unmuted"
            )
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        )
        await ctx.send(embed=embed)
        
    
    ### Clear a channels messages by some amount ###
    @commands.command()
    async def clear(self, ctx, amount=10):
        """
        Delete the amount specified messeges on channel
        """
        filename = f"{ctx.channel.name}_clear.txt" # Make text file
        with open(filename, "w") as file:
            file.write(f"{ctx.author} cleared {amount} messages of {ctx.channel.name} in {ctx.channel.category.name}\n\n") # Log action
            async for msg in ctx.channel.history(limit=amount): # Go through channels messages
                try:
                    file.write(f"{msg.created_at} - {msg.author.display_name}: {msg.clean_content}\n") # Log the deleted text
                except:
                    file.write(f"{msg.created_at} - {msg.author.display_name}: Message could not be displayed\n")
        await ctx.channel.purge(limit=amount) # Delete messages
        await self.hiddenLogRoom.send(file=discord.File(filename)) # Post the delete log
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
        await self.hiddenLogRoom.send(embed=embed) # Log what the error was
    
    
    ### Clear a channel's messages by some amount for some user ###
    @commands.command()
    async def purge(self, ctx, member:discord.Member, amount=10):
        """
        Delete Messeges of a specific user
        """
        filename = f"{member.display_name}_purge.txt" # Make a text file

        def is_m(m): # Checks if messages author is the member being purged
            return m.author == member and m.author != self.bot.user

        with open(filename, "w", encoding="UTF-8") as file:
            file.write(f"{ctx.author} cleared {amount} messages of {member.display_name} in {ctx.channel.name}\n\n") # Log action
            
            for channel in self.guild.text_channels: # Go through all text channels of guild
                file.write(f"\nMessages from {channel.name} in {channel.category.name}:\n") # Break up the logs by channel
                async for msg in channel.history(limit=amount): # Go through channel's messages
                    if msg.author == member:
                        try:
                            file.write(f"{msg.created_at} - {msg.author.display_name}: {msg.clean_content}\n") # Log the deleted text
                        except:
                            file.write(f"{msg.created_at} - {msg.author.display_name}: Message could not be displayed\n")
                await channel.purge(limit=amount, check=is_m) # Delete messages of member
        await self.hiddenLogRoom.send(file=discord.File(filename)) # Post the delete log
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
        await self.hiddenLogRoom.send(embed=embed) # Log what the error was



def setup(bot):
    bot.add_cog(Mod(bot))