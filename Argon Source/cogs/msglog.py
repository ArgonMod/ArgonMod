import discord 
from discord.ext import commands 
from pymongo import MongoClient  as mcl
import os 
import sys
from datetime import datetime 

class MsgLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = mcl(self.bot.mongodb)
        self.db = self.client['modtest']
        self.col = self.db['modlog']
        self.settings = self.db['settings']
        self.config=self.db['automod']

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        myquery = {"server-id": str(message.guild.id)}
        mydoc = self.config.find(myquery)
        found=False
        for x in mydoc:
            found=True
        if not found:
            return
        if x["msg-del"]=="no" or x["msglog"]=="None":
            return
        try:
            log=self.bot.get_channel(int(x["msglog"]))
        except:
             return
        embed = discord.Embed(color=0x551A8B, timestamp=datetime.utcnow())
        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name=f"Message deleted in {message.channel}", value=message.content)
        return await log.send(embed=embed)
    @commands.Cog.listener()
    async def on_bulk_message_delete(self,messages):
        message=messages[0]
        myquery = {"server-id": str(message.guild.id)}
        mydoc = self.config.find(myquery)
        found=False
        for x in mydoc:
            found=True
        if not found:
            return
        if x["msg-del"]=="no" or x["msglog"]=="None":
            return
        try:
            log=self.bot.get_channel(int(x["msglog"]))
        except:
             return
        mlist=""
        for msg in messages:
            mlist+=msg.content+"\n"
        embed = discord.Embed(color=0x551A8B, timestamp=datetime.utcnow())
        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
        embed.add_field(name=f"Multiple messages deleted in {message.channel}", value=mlist)
        return await log.send(embed=embed)
    @commands.Cog.listener()
    async def on_message_edit(self,before,after):
        if not before.guild or not after.guild:
            return
        if before.content=="" or after.content=="":
            return
        if before.content==after.content:
            return
        myquery = {"server-id": str(before.guild.id)}
        mydoc = self.config.find(myquery)
        found=False
        for x in mydoc:
            found=True
        if not found:
            return
        if x["msg-edit"]=="no" or x["msglog"]=="None":
            return
        try:
            log=self.bot.get_channel(int(x["msglog"]))
        except:
             return
        try:
            embed = discord.Embed(color=0x57A2FF, timestamp=datetime.utcnow())
            embed.set_author(name=before.author, icon_url=before.author.avatar_url)
            embed.add_field(name=f"Message edited in {before.channel}", value=f"""
            **Before:** {before.content}
            **+After:** {after.content}
            """)
            return await log.send(embed=embed)
        except:
            pass
        


def setup(bot):
    bot.add_cog(MsgLog(bot))
