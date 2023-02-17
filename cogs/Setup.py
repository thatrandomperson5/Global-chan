from discord.ext import commands
import aiohttp
import discord
import sys
import asqlite
import asyncio
sys.path.append("..")
from chunks import rqEmbed


class SetupTools(commands.Cog, description="Setup tools for global-chan"):
    def __init__(self, bot):
        self.bot = bot 
        self.avt = "https://cdn.discordapp.com/avatars/1006675473134268456/dde24889dfc1efaee8c796fe2522acbe.png?size=1024"
    
        

                
    def stembed(self, ctx, stage, error=False):
        embed = rqEmbed(ctx, title="Setting up global channel", description="We're setting up, wait just a moment!")
        stages =["Cleaning up","Creating channel", "Creating webhook", "Establishing webhook"]
        i = 1
        val = ""
        for x in stages:
            if i > stage:
                val += "❌ "+x+"\n"
            
            else:
                val += "✅ "+x+"\n"
            i+=1
        embed.add_field(name="Process", value=val)
        if error:
            out = []
            for x in error.split("\n"):
                out.append("- "+x)
            out = "\n".join(out)
            embed.add_field(name="Error", value=f"```diff\n{out}\n```", inline=False)
        return embed
    class SetupFlags(commands.FlagConverter):
        hook_name: str="Global Chan"
        delete_old_channel: bool=True
    @commands.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def setup_(self, ctx, channel_name="Global Channel", *, flags: SetupFlags):
        """Setup a new Global Channel
        If one already exists then delete that one or remove webhook.
        Flags:
            `[hook_name: Global Chan]`
            `[delete_old_channel: True]`
        Flags called like: `flagname:value`
        """
        conn = await asqlite.connect("gch.db")
        message = await ctx.send(embed=self.stembed(ctx, 0))
        try:
            async with conn.cursor() as curr:
                await curr.execute("SELECT channel FROM chanList WHERE guild = ?", ctx.guild.id)
                data = await curr.fetchall()
            
                if not len(data) == 0:
                    data = int(data[0][0])
                    chan = self.bot.get_channel(data)
                    
                    if flags.delete_old_channel:
                        await chan.delete()
                    else:
                        hooks = await chan.webhooks() 
                        await hooks[0].delete()
        except Exception as e:
            await message.edit(embed=self.stembed(ctx, 0, str(e)))
            await conn.close()
            return
        await message.edit(embed=self.stembed(ctx, 1))
        try:
            channel = await ctx.guild.create_text_channel(channel_name)
        except Exception as e:
            await message.edit(embed=self.stembed(ctx, 1, str(e)))
            await conn.close()
            return
        await message.edit(embed=self.stembed(ctx, 2))
        print("1")
        try:
            webhook = await channel.create_webhook(name=flags.hook_name, reason="Setup for global channel")
        except Exception as e:
            await message.edit(embed=self.stembed(ctx, 2, str(e)))
            await conn.close()
            return    
            
        await message.edit(embed=self.stembed(ctx, 3))
        try:
            async with conn.cursor() as curr:
                await curr.execute("""REPLACE INTO chanList(guild, channel, blacklisted, webhook)
                VALUES(?, ?, 0, ?);""", ctx.guild.id, channel.id, webhook.url)
        
        except Exception as e:
            
            await message.edit(embed=self.stembed(ctx, 3, str(e)))
            await conn.close()
            return 
        await conn.commit()
        print(2)
        await message.edit(embed=self.stembed(ctx, 4))
        
        await conn.close()
        #Testing
        async with asqlite.connect('gch.db') as conn:
           async with conn.cursor() as curr:
               await curr.execute("""SELECT webhook FROM chanList WHERE guild = ?;""", ctx.guild.id)
               data = await curr.fetchall()
               data = data[0][0]
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(data, session=session)
            embed=discord.Embed(title="Global channel successfully setup!", description="Some messages will be poppin through here soon. Delete the global channel with `gchan?unregister`", color=0x03e200)
            await webhook.send(embed=embed, avatar_url=self.avt)
            await asyncio.sleep(3)
            embed=discord.Embed(color=0x4b008c, timestamp=discord.utils.utcnow())
            embed.set_footer(text=f"Sent from {ctx.guild.name}", icon_url=ctx.guild.icon)
            await webhook.send("Messages will look like this!",embed=embed)


            
        
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unregister(self, ctx):
        """Take down a global channel. 
        This is the recommend method to delete your global channel.
        """
        async with asqlite.connect('gch.db') as conn:
           async with conn.cursor() as curr:
               await curr.execute("""SELECT channel FROM chanList WHERE guild = ?;""", ctx.guild.id)
               data = await curr.fetchall()
               data = data[0][0]
               channel = self.bot.get_channel(int(data))
               await curr.execute("""DELETE FROM chanList WHERE guild = ?;""", ctx.guild.id)
               await conn.commit()
        await channel.delete()
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        async with asqlite.connect('gch.db') as conn:
           async with conn.cursor() as curr:
               await curr.execute("""SELECT * FROM chanList WHERE channel = ?;""", channel.id)
               data = await curr.fetchall()
               if len(data) > 0:
                   await curr.execute("""DELETE FROM chanList WHERE channel = ?;""", channel.id)
async def setup(bot):
	await bot.add_cog(SetupTools(bot))