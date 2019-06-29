import discord 
from discord.ext import commands 
from pymongo import MongoClient  as mcl
import os 
import sys
import re
import asyncio

DISCORD_INVITE = r'discord(?:app\.com|\.gg)[\/invite\/]?(?:(?!.*[Ii10OolL]).[a-zA-Z0-9]{5,6}|[a-zA-Z0-9\-]{2,32})'
class AntiLink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = mcl(self.bot.mongodb)
        self.db = self.client['modtest']
        self.col = self.db['modlog']
        self.settings = self.db['settings']
        self.config=self.db['automod']

    @commands.Cog.listener()
    async def on_message(self,message):
        if str(message.author)=="Argon#4279":
            return
        if "!config" in str(message.content):
            return
        invite=False
        found=False
        channel=False
        myquery = {"server-id": str(message.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
            found=True
        if not found:
            return
        ignore=False
        if x["anti-invite"]=="yes":
            invite=True
        if x["ignore"]!="none":
            ignore=True
            ignore1=message.guild.get_role(int(x["ignore"]))
        if x["modlog"]!="None":
            channel=True
            chan=self.bot.get_channel(int(x["modlog"]))
        modwarn=False
        if x["warn-mod"]!="no":
            modwarn=True
        if ignore:
            try:
                if (ignore1 in message.author.roles):
                    return
            except:
                pass
        if not invite:
            return
        regex = re.compile(DISCORD_INVITE)
        invites = regex.findall(message.content)
        if invites:
            await message.delete()
            await message.channel.send(F"{self.bot.x}{message.author.mention} No invites in this server. Who do you think you are?", delete_after=3)       
            
            
        if channel:
            #CHAN is channel variable...send message in mod channel
            pass
        if modwarn:
            #Record as warning
            pass


def setup(bot):
    bot.add_cog(AntiLink(bot))
