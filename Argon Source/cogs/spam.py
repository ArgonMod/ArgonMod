import discord 
from discord.ext import commands 
from pymongo import MongoClient as mcl
import asyncio
from datetime import datetime, timedelta
import time
from time import gmtime, strftime
from collections import defaultdict
    
import base64
import binascii
import logging
import re
import struct
from datetime import datetime
import typing 

def convtime(time: str):
    ld = 86400
    lh = 3600
    lm = 60
    ls = 1
    letters = {
        "d": ld,
        "h": lh,
        "m": lm,
        "s": ls
    }
    timet = [i for i in re.split(r'(\d+)', time) if i]
    timelst = [int(i)*letters[j] for i,j in zip(timet[::2],timet[1::2])]
    return sum(timelst)

class Anti_Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.client = mcl("mongodb://o:o99999@ds337377.mlab.com:37377/modtest")
        self.db = self.client['modtest']
        self.col = self.db['modlog']
        self.settings = self.db['settings']
        self.muted = self.db["muted"]
        self.warndb = self.db['warning']
        self.config=self.db['automod']
        self.spam = self.db['spam']
    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            myquery = {"server-id": str(message.guild.id)}
            mydoc = self.config.find(myquery)
            server = message.guild
            ignore1=False
            for x in mydoc:
                ignore=server.get_role(x['ignore'])
                if ignore:
                    ignore1=True
            guild = message.guild
            
            self.data = self.spam.find_one()
            if not str(guild.id) in self.data:
                return 
            spam = self.data[str(guild.id)]["anti-spam"]
            if spam == "disabled":
                return
            try:
                if ignore1:
                    if ignore in message.author.roles:
                        return
            except:
                pass
            x = message.content
            if len(x)==0:
                return
            total = len([i for i in x if i.isupper()])/len(x)
            if len(message.content) > 3 and  total >= .7:
                await message.delete()
                await message.channel.send(f"{self.bot.x} {message.author.mention} Do not cap spam!", delete_after=3)
        except:
            pass

    

def setup(bot):
    bot.add_cog(Anti_Spam(bot))
