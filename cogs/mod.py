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
                embed=discord.Embed(title="Jarvis:", color=0x00ff40)
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
            embed=discord.Embed(title="Jarvis:", color=0x00ff40)
            embed.add_field(
                name="Mute", 
                value="You do not have permision to do that", 
                inline=True
                )
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Mod(bot))