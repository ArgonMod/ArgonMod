import discord 
from discord.ext import commands 
from pymongo import MongoClient  as mcl
import os 
import discord 
from discord.ext import commands 
from pymongo import MongoClient  as mcl
import os 
import sys
from config import *

TOKEN = token

cogs = [
    'cogs.config',
    'cogs.automod',
    'cogs.help',
    'cogs.utility',
    'cogs.verify',
    'cogs.autolog',
    'cogs.msglog',
    'cogs.chanlog',
    'cogs.memlog',
    'cogs.rolelog',
    'cogs.swear',
    'cogs.invite',
    'cogs.spam',
    'cogs.link',
    'cogs.sowner',
    'cogs.anti-spam',
    'cogs.mod'
]


def prefix(bot, message):
    return bprefix

class Argon(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=prefix, case_insensitive=True)

        self.check = scheck
        self.x = sx
        self.settings = ssettings
        self.embed = sembed
        self.enabled= senabled
        self.disabled= sdisabled
        self.mongodb='mongodb://o:o99999@ds337377.mlab.com:37377/modtest'
        self.prefix=bprefix

    async def on_ready(self):
        print(f"Online!\nPrefix: {bprefix}")
        for cog in cogs:
            try:
                bot.load_extension(cog)
                print(f"Loaded {cog} successfully.")
            except Exception as e:
                print(e)
        await bot.change_presence(activity = discord.Game("{:,} servers".format(len(bot.guilds)), type=discord.ActivityType.watching))



bot = Argon()
bot.remove_command('help')
@bot.command()
@commands.is_owner()
async def restart(ctx):
    await ctx.send(F"Restarting. This may take a little! Please be patient with me.")
    await bot.change_presence(status = discord.Status.dnd, activity = discord.Game("RESTARTING BOT!"))
    os.execv(sys.executable, ['python3.6'] + sys.argv)

@bot.command()
@commands.is_owner()
async def reload(ctx, *, cog = None):
    errors = ""
    if cog is None:
        for cog in cogs:
            try:
                bot.reload_extension(cog)
            except Exception as e:
                errors += f"""
                **{cog}**: `{e}`\n
                """
        await ctx.send(f"{bot.check} Successfully reloaded {len(cogs)} cogs.")
        if not errors:
            return
        await ctx.send(errors)
    try:
        bot.reload_extension(cog)
        await ctx.send(f"{bot.check} Successsfully reloaded **{cog}**.")
    except Exception as e:
        errors += f"""
        **{cog}**: `{e}`\n
        """
    if not errors:
        return
    await ctx.send(errors)
@bot.event
async def on_command_error(ctx, error):
    pass
bot.run(TOKEN)
