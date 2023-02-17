import discord
from discord.ext import commands
import os
from chunks import rqEmbed
from ezHelp.utils import cogSplit
import ezHelp
from sa import keep_alive
import asqlite
#Invite https://discord.com/api/oauth2/authorize?client_id=1006675473134268456&permissions=536988752&scope=bot
description = """
"""
class Bot(commands.Bot):
  
    async def setup_hook(self):
        async with asqlite.connect('gch.db') as conn:
            async with conn.cursor() as curr:
                await curr.execute("""CREATE TABLE IF NOT EXISTS chanList(
                guild INT PRIMARY KEY,
                channel INT,
                blacklisted INT,
                webhook TEXT)
                """)
                await conn.commit()
        for f in os.listdir("./cogs"):
	        if f.endswith(".py"):
		        await bot.load_extension("cogs." + f[:-3])
intents = discord.Intents.all()
bot = Bot(command_prefix=commands.when_mentioned_or("gchan?"), description=description, intents=intents)

class disHelp(ezHelp.dynHelp):
    def on_page(self, commands, page, last_page):
        commands = list(commands)
        embed = rqEmbed(self.context, title=f"Global Chan {commands.pop(len(commands)-1)[1]} [{page+1}/{last_page}]")
        
        for x in commands:
            index = x[0]
            command = x[1]
            
            embed.add_field(name=f"{index}) {self.get_command_signature(command)}", value=command.short_doc,inline=False)
        return embed
    def on_main(self, commands, page, last_page):
        #if self.no_category
        embed = rqEmbed(self.context, title=f"Global Chan [{page+1}/{last_page}]")
        
        
        name = None
        value = ""
        for x in commands:
            
            index = x[0]
            x = x[1]
            if x["type"] == "cog":
                if name is not None:
                    
                    embed.add_field(name=name, value=value, inline=False)
                else:
                    embed.description = value
                if x["value"] is None:
                    name=self.no_category
                else:
                    name = x["value"].qualified_name
                value = ""
            elif x["type"] == "command":
                v: commands.Command = x.get("value")
               
                value += f"{index})  {v}: `{self.get_command_signature(v)}`\n{v.short_doc}\n"
        if name is not None:
            if value == "":
                value= "\u200b"
            embed.add_field(name=name, value=value, inline=False)
        else:
            embed.description = value
        return embed
    async def send_command_help(self, command):
        embed = rqEmbed(self.context, title=str(command), description=command.help)
        embed.add_field(name="Usage", value=f"`{self.get_command_signature(command)}`")
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)
        await self.context.reply(embed=embed, mention_author=False)  
        
bot.help_command = disHelp(no_category = 'Informational', commands=cogSplit)

@bot.event
async def on_ready():
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print(f"pfpsrc: {bot.user.avatar}")

    

@bot.command()
async def invite(ctx):
    """Invite this bot to your own server!"""
    embed = rqEmbed(ctx, title="Add global chan to your server!", description="Connect with people from other server on your global channel!")
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Invite Me!\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800",style=discord.ButtonStyle.link,url="https://discord.com/api/oauth2/authorize?client_id=1006675473134268456&permissions=536988752&scope=bot"))
    await ctx.reply(embed=embed, view=view, mention_author=False)

@bot.command()
async def close(ctx):
    """You don't need to know what this does"""
    if ctx.author.id == 910899642236043294:
        
        await ctx.send("Closed")
        await bot.close()
    else:
        await ctx.send("You don't have the permission to do that!")


keep_alive()
bot.run(os.getenv("TOKEN"))