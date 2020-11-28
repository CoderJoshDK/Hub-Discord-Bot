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
        self.reportRoom = get(self.guild.channels, id=782084427022991451)

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

    ### Mute someone ###
    @commands.command()
    async def mute(self, ctx, member : discord.Member, time="5m", *, reason="spam"):
        # Only a mod or above can mute
        if ctx.author.top_role >= get(self.guild.roles, name="Mod"):
            
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
                    value=f"{member.name} has been muted for {time} because of {reason} by {ctx.author.name}", 
                    inline=True
                )
                await ctx.send(embed=embed)
                
                ### Mute them and then unmute them after time ###
                muted_role = get(ctx.guild.roles, name="Muted")
                member_role = get(ctx.guild.roles, name="Member")

                await member.add_roles(muted_role, reason=reason) # Make them muted
                await member.remove_roles(member_role) # Member roles can type so get rid of it

                await asyncio.sleep(seconds)

                await member.remove_roles(muted_role, reason="Time is up")
                await member.add_roles(member_role) # Make them a member again
                
                # Unmute embed
                embed=discord.Embed(title="Jarvis:", color=0x00ff40)
                embed.add_field(
                    name="Unmuted", 
                    value=f"{member.name} has been unmuted. {time} has past", 
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
        else: # Does not have the power to mute someone
            embed=discord.Embed(title="Jarvis:", color=0xf22929)
            embed.add_field(
                name="Mute", 
                value="You do not have permision to do that", 
                inline=True
                )
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
        if ctx.author.top_role >= get(self.guild.roles, name="Mod"):
            muted_role = get(ctx.guild.roles, name="Muted")
            member_role = get(ctx.guild.roles, name="Member")

            await member.remove_roles(muted_role, reason="Bot reloaded")
            await member.add_roles(member_role)
            
            embed = discord.Embed(color=discord.Color.dark_green)
            embed.add_field(
                name="Unmute",
                value=f"{member.name} has been unmuted"
            )
        else:
            embed = discord.Embed(color=discord.Color.dark_red)
            embed.add_field(
                name="Unmute",
                value="You do not have permision to do that"
            )

        await ctx.send(embed=embed)

    ### Report a users for doing something bad ###
    @commands.command()
    async def report(self, ctx, member:discord.Member, *, reason):
        await self.reportRoom.send(f"<@!{ctx.author.id}> has reported <@!{member.id}> because of {reason}")
        await ctx.author.send("Thank you for reporting. We will look into it and press action if needed")
        await ctx.message.delete()
    
    ### If they report wrong ###
    @report.error
    async def report_error(self, ctx, error):
        await ctx.author.send("You have tried to report a user but did something wrong. To use correctly, type [!report @user they did something bad]. We will look into it and get back to you")
        await ctx.message.delete()
        
def setup(bot):
    bot.add_cog(Mod(bot))