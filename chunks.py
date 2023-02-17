import discord

class rqEmbed(discord.Embed):
    def __init__(self, ctx, **kwargs):
        super().__init__(**kwargs, timestamp=discord.utils.utcnow(), color=discord.Color.from_rgb(47, 212, 63))
        self.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar)