import discord 
from discord.ext import commands 
from pymongo import MongoClient  as mcl
import os 
import sys

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
        swear=False
        channel=False
        ignore=False
        myquery = {"server-id": str(message.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
            found=True
        if not found:
            return
        modwarn=False
        if x["warn-mod"]!="no":
            modwarn=True
        if x["anti-swear"]=="yes":
            swear=True
        if x["ignore"]!="none":
            ignore=True
            ignore1=message.guild.get_role(int(x["ignore"]))
        if x["modlog"]!="None":
            channel=True
            chan=self.bot.get_channel(int(x["modlog"]))
        if ignore:
            try:
                if (ignore1 in message.author.roles):
                    return
            except:
                pass
        if not swear:
            return
        bad=x['bad-words']
        good=x['good-words']
        msg=str(message.content)
        msg=msg.replace(" ","")
        for j in range(len(good)):
            msg=msg.replace(good[j],"")
            for j in range(len(bad)):
                 if bad[j] in msg:
                     await message.channel.send(str(message.author.mention)+" watch your language!")
                     await message.delete()
                 if channel:
                     #CHAN is channel variable...send message in mod channel
                     pass
    


def setup(bot):
    bot.add_cog(AntiLink(bot))
