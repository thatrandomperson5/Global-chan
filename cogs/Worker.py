from discord.ext import tasks, commands
import discord
import asqlite
from dataclasses import dataclass
import datetime
import aiohttp
import io
import traceback

import sys
sys.path.append("..")
from chunks import rqEmbed


class Worker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.avt = "https://cdn.discordapp.com/avatars/1006675473134268456/dde24889dfc1efaee8c796fe2522acbe.png?size=1024"
        self.mcache = []
    @commands.command(name="workerstats")
    async def workerstats(self, ctx):
        """Send the worker cog stats"""
        embed=rqEmbed(ctx, title="Worker Data")
        embed.add_field(name="Cached Messages", value="Currently there are {} cached messages.".format(len(self.mcache)), inline=False)
        await ctx.send(embed=embed)

    @dataclass
    class CacheItem:
        avatar: str
        user: str
        exemptions: list
        message: str
        attachments: list
        time: datetime.datetime
        guild_avt: str
        guild: str
     
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        ctx = await self.bot.get_context(message)
        async with asqlite.connect('gch.db') as conn:
           async with conn.cursor() as curr:
               await curr.execute("""SELECT channel FROM chanList WHERE guild = ?;""", ctx.guild.id)
               data = await curr.fetchall()
        if len(data) < 1:
            return
        data = data[0]
        if (
            message.channel.id in data
            and not message.author.bot
            and not ctx.valid
            and not ctx.prefix
        ):
            self.mcache.append(self.CacheItem(
                str(ctx.author.avatar),
                str(ctx.author),
                [message.channel.id],
                message.content,
                message.attachments,
                discord.utils.utcnow(),
                str(ctx.guild.icon),
                str(ctx.guild.name),
               
            ))
    async def broadcast(self, item, joint):
        message = item.message
        if item.guild_avt == "None":
            item.guild_avt = None
        async def url2discord(url, session):
            
            async with session.get(url.url) as resp:
                if resp.status != 200:
                    with open("404.png", "rb") as f:
                        return discord.File(f)
                data = io.BytesIO(await resp.read())
                return discord.File(data, url.filename)

                    
        async with aiohttp.ClientSession() as session:
            item.attachments = [await url2discord(x, session) for x in item.attachments]
        embed=discord.Embed(color=0x4b008c, timestamp=item.time)
        embed.set_footer(text=f"Sent from {item.guild}", icon_url=item.guild_avt)
        kwargs = {"embed": embed, 
                  "files": 
                  item.attachments, 
                  "username":item.user, 
                  "avatar_url": item.avatar
                 }
        print(item.guild_avt)
        async with aiohttp.ClientSession() as session:
            for x, y in joint:
                webhook = discord.Webhook.from_url(y, session=session)
                await webhook.send(message, **kwargs)

    @tasks.loop(seconds=1.0)
    async def dumper(self):
        i = 0
        for x in self.mcache:
            if i == 5:
                break
            item: self.CacheItem = self.mcache.pop(self.mcache.index(x))
            async with asqlite.connect('gch.db') as conn:
                   async with conn.cursor() as curr:
                       await curr.execute("""SELECT channel, webhook FROM chanList""")
                       data = await curr.fetchall()
                       joint = list(data)
            joint = [tuple(x) for x in joint if not int(x[0]) in item.exemptions]
     
            try:
                await self.broadcast(item, joint)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__,file=sys.stdout)
                self.mcache.insert(0, item)
                break
            i+=1
    @dumper.before_loop
    async def dump_checks(self):
        await self.bot.wait_until_ready()

    async def cog_load(self):
        self.dumper.start()
    async def cog_unload(self):
        self.dumper.cancel()
        
async def setup(bot):
	await bot.add_cog(Worker(bot))