import discord 
from discord.ext import commands 
from pymongo import MongoClient  as mcl
import os 
import sys
import re

LINKS = r'^https?:\/\/.*[\r\n]*'
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
        link=False
        myquery = {"server-id": str(message.guild.id)}
        channel=None
        mydoc = self.config.find(myquery)
        for x in mydoc:
            found=True
        if not found:
            return
        ignore=False
        modwarn=False
        if x["warn-mod"]!="no":
            modwarn=True
        if x["anti-link"]=="yes":
            link=True
        if x["ignore"]!="none":
            ignore=True
            ignore1=message.guild.get_role(int(x["ignore"]))
        if x["modlog"]!="None":
            channel=True
            chan=self.bot.get_channel(int(x["modlog"]))
        try:
            if ignore:
                if (ignore1 in message.author.roles):
                    return
        except:
            pass
        if not link:
            return
        regex = re.compile(LINKS)
        links = regex.findall(message.content)
        if links:
            await message.delete()
            await message.channel.send(F"{self.bot.x}{message.author.mention} No links in this server. Who do you think you are?", delete_after=3)
            
        if channel:
            #CHAN is channel variable...send message in mod channel
            pass
        if modwarn:
            #Record as warning
            pass
    


def setup(bot):
    bot.add_cog(AntiLink(bot))
