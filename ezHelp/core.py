from discord.ext import menus
import discord
from discord.ext import commands
from itertools import chain

class MyMenuPages(discord.ui.View, menus.MenuPages):
    def __init__(self, source, *, delete_message_after=False, timeout=120):
        super().__init__(timeout=timeout)
        self._source = source
        self.current_page = 0
        self.ctx = None
        self.message = None
        self.delete_message_after = delete_message_after

    async def start(self, ctx, *, channel=None, wait=False):
        # We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
        await self._source._prepare_once()
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx, ctx.channel)

    async def _get_kwargs_from_page(self, page):
        """This method calls ListPageSource.format_page class"""
        value = await super()._get_kwargs_from_page(page)
        if 'view' not in value:
            value.update({'view': self})
        return value

    async def interaction_check(self, interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author

    @discord.ui.button(emoji='⏮', style=discord.ButtonStyle.grey)
    async def first_page(self, interaction, button):
        await self.show_page(0)
        await interaction.response.defer()

    @discord.ui.button(emoji='◀️', style=discord.ButtonStyle.grey)
    async def before_page(self, interaction, button):
        await self.show_checked_page(self.current_page - 1)
        await interaction.response.defer()

    @discord.ui.button(emoji='🔒', style=discord.ButtonStyle.red)
    async def stop_page(self, interaction, button):
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop()
        if self.delete_message_after:
            await self.message.delete(delay=0)

        
    @discord.ui.button(emoji='▶️', style=discord.ButtonStyle.grey)
    async def next_page(self, interaction, button):
        await self.show_checked_page(self.current_page + 1)
        await interaction.response.defer()

    @discord.ui.button(emoji='⏭', style=discord.ButtonStyle.grey)
    async def last_page(self, interaction, button):
        await self.show_page(self._source.get_max_pages() - 1)
        await interaction.response.defer()
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
def enum(iter, *, start):
    i = start
    out = []
    for x in iter:
        if type(x) == dict:
            if "IGNOREFLAG" in x.keys():
                out.append((-1, x))
            else:
               out.append((i, x))
               i +=1                
        else:
            out.append((i, x))
            i +=1               

    return out  
class HelpPageSource(menus.ListPageSource):
    def __init__(self, data, helpcommand, *, per_page=6, callback=None):
        
        super().__init__(data, per_page=per_page)
        self.helpcommand = helpcommand
        self.cb = callback
        if self.cb == None:
            self.cb = helpcommand.on_page
    
    
    async def format_page(self, menu, entries):
        
        page = menu.current_page
        max_page = self.get_max_pages()
        starting_number = page * self.per_page + 1
        
        embed = self.cb(enum(entries, start=starting_number), page, max_page)
        
        return embed
        
class Help(commands.MinimalHelpCommand):
    def __init__(self, *, commands=None, per_page=6, delete_message_after=False, timeout=120, **kwargs):
        self.ez_cmds = commands
        self.ez_per_page = per_page
        self.ez_delete_message_after = delete_message_after
        self.ez_timeout = timeout
        super().__init__(**kwargs)
    async def send_bot_help(self, mapping):
        if not self.ez_cmds:
            all_commands = list(chain.from_iterable(mapping.values()))
        else:
            all_commands = self.ez_cmds(mapping)
        
        formatter = HelpPageSource(all_commands, self, per_page=self.ez_per_page)
        menu = MyMenuPages(formatter, delete_message_after=self.ez_delete_message_after, timeout=self.ez_timeout)
        await menu.start(self.context)
class cogHelp(commands.MinimalHelpCommand):
    def __init__(self, *, commands=None, per_page=6, delete_message_after=False, timeout=120, **kwargs):
        self.ez_cmds = commands
        self.ez_per_page = per_page
        self.ez_delete_message_after = delete_message_after
        self.ez_timeout = timeout
        super().__init__(**kwargs)
    async def send_cog_help(self, cog):
        if not self.ez_cmds:
            all_commands = cog.get_commands()
            all_commands.append(cog.qualified_name)
        else:
            all_commands = self.ez_cmds(cog)
        formatter = HelpPageSource(all_commands, self, per_page=self.ez_per_page)
        menu = MyMenuPages(formatter, delete_message_after=self.ez_delete_message_after, timeout=self.ez_timeout)
        await menu.start(self.context)
class dynHelp(commands.MinimalHelpCommand):
    def __init__(self, *, commands=None, per_page=6, delete_message_after=False, timeout=120, **kwargs):
        self.ez_cmds = commands
        self.ez_per_page = per_page
        self.ez_delete_message_after = delete_message_after
        self.ez_timeout = timeout
        super().__init__(**kwargs)
    async def send_bot_help(self, mapping):
        if not self.ez_cmds:
            all_commands = list(chain.from_iterable(mapping.values()))
        else:
            all_commands = self.ez_cmds(mapping)
        formatter = HelpPageSource(all_commands, self, per_page=self.ez_per_page, callback=self.on_main)
        menu = MyMenuPages(formatter, delete_message_after=self.ez_delete_message_after, timeout=self.ez_timeout)
        await menu.start(self.context)
    async def send_cog_help(self, cog):
        if not self.ez_cmds:
            all_commands = cog.get_commands()
            all_commands.append(cog.qualified_name)
        else:
            all_commands = self.ez_cmds(cog)
        formatter = HelpPageSource(all_commands, self, per_page=self.ez_per_page)
        menu = MyMenuPages(formatter, delete_message_after=self.ez_delete_message_after, timeout=self.ez_timeout)
        await menu.start(self.context)
