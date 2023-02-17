import discord

def onmap(map):
    out = []
    
    for x, y in list(map.items()):
        
        out.append({"type": "cog", "value": x, "IGNOREFLAG": True})
        for z in y:
            out.append({"type": "command", "value": z})
    
    return out
def oncog(cog):
    all_commands = cog.get_commands()
    all_commands.append(cog.qualified_name)
    return all_commands
def cogSplit(map):
    """Makes cog mapping able to be paginated"""
    
    if isinstance(map, discord.ext.commands.Cog):
        return oncog(map)
    else:
        return onmap(map)