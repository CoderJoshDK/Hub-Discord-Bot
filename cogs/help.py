import discord
from discord.ext import commands

from utils.util import Pag # pylint: disable=import-error

import re
import math
import random

class Help(commands.Cog):

    ### On start of code ###
    def __init__(self, bot):
        self.bot = bot
        self.cmds_per_page = 6

    def return_sorted_commands(self, commandList):
        '''
        Sort a list of commands in alphabetic order by name
        Return that sorted list
        '''
        return sorted(commandList, key=lambda x: x.name)

    def get_commands_signature(self, command: commands.Command, ctx: commands.Context):
        '''
        Return a string formated to desplay how to use the command
        Params:
         - command (commands.Command) : The command to look at on how to use
         - ctx (context object) : Used for getting the prefix of the guild
        '''
        # Some commands have multiple names that can be used
        aliases = "|".join(command.aliases)
        # The names that can be used to invoke the command
        cmd_invoke = f"[{command.name}|{aliases}]" if command.aliases else command.name

        # Everything needed to invoke the command but not with the name
        full_invoke = command.qualified_name.replace(command.name, "")

        # Full instructions on how to call the command including the signature
        # The signature is the params of a function
        signature = f"{ctx.prefix}{full_invoke}{cmd_invoke} {command.signature}"
        return signature

    async def return_filtered_commands(self, walkable, ctx):
        '''
        Helper command to getting all the commands in a set

        Params:
         - walkable (Cog, group, or bot) : iterate over to find all the commands attached
         - ctx (context object) : Used for sending msgs and knowing location
        Returns:
         - filtered (list) : All available commands in alphabetic order
        '''
        filtered = []

        for c in walkable.walk_commands():
            try:
                # Go past hidden and subcommands
                if c.hidden:
                    continue
                elif c.parent:
                    continue
                
                # Only add the command to list if the user can run it
                await c.can_run(ctx)
                filtered.append(c)
            except commands.CommandError:
                # Error trigered by the can_run function if the user can not use the command
                continue
        
        return self.return_sorted_commands(filtered)

    async def setup_help_pag(self, ctx, entity=None, title=None):
        """
        Helper command to building the help page

        Params:
         - ctx (context object) : Used for sending msgs and knowing location
         - Optional Params :
            - entity (command, cog, or group object) : group to find help info for
            - title (string): Name of section
        """
        entity = entity or self.bot
        title = title or self.bot.description

        # All the pages to flip through with the buttons
        pages = []

        # If the entity is a command, the filtered_commands is all the commands asociated
        if isinstance(entity, commands.Command):
            filtered_commands = (
                list(set(entity.all_commands.values()))
                if hasattr(entity, "all_commands")
                else []
            )
            filtered_commands.insert(0, entity)
        
        # Entity is a group so get the commands under the group
        else:
            filtered_commands = await self.return_filtered_commands(entity, ctx)

        # Go through all the commands and display the cmd_per_page amt
        for i in range(0, len(filtered_commands), self.cmds_per_page):
            next_commands = filtered_commands[i : i + self.cmds_per_page]
            commands_entry = ""

            # Go through all the cmds on the given page
            for cmd in next_commands:
                desc = cmd.short_doc or cmd.description
                signature = self.get_commands_signature(cmd, ctx)
                subcommand = "Has subcommands" if hasattr(cmd, "all_commands") else ""
                
                commands_entry += (
                    f"• **__{cmd.name}__**\n```\n{signature}\n```\n{desc}\n"
                    if isinstance(entity, commands.Command)
                    else f"• **__{cmd.name}__**\n{desc}\n    {subcommand}\n"
                )
            pages.append(commands_entry)

        # Pages with buttons to flip through
        await Pag(title=title, color=0xCE2029, entries=pages, length=1).start(ctx)
        

    @commands.command(
        name='help',
        aliases=['h', 'commands'],
        description='The help command'
    )
    async def help_command(self, ctx, *, entity=None):
        '''
        Displays a help page that can be flipped through
        Params:
         - ctx (context object) : Used for sending msgs and knowing location
         - Optional Params :
            - entity (command, cog, or group object) : group to find help info for
        '''
        # If no entity is given, display the help page with all commands
        if not entity:
            await self.setup_help_pag(ctx)
        else:
            # If entity is a cog, display help page with commands inside of cog
            cog = self.bot.get_cog(entity)
            if cog:
                await self.setup_help_pag(ctx, cog, f"{cog.qualified_name}'s commands")

            else:
                # If entity is a command, display the usage of a command
                command = self.bot.get_command(entity)
                if command:
                    await self.setup_help_pag(ctx, command, command.name)
                
                # If all else failes, must be the user giving us bad info so we should tell them
                else:
                    await ctx.send(f"Invalid entry {entity} for the help command")
    
    


def setup(bot):
    bot.add_cog(Help(bot))