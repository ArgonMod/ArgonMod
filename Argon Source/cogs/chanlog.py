import discord 
from discord.ext import commands 
from pymongo import MongoClient  as mcl
import os 
import sys

class ChanLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = mcl(self.bot.mongodb)
        self.db = self.client['modtest']
        self.col = self.db['modlog']
        self.settings = self.db['settings']
        self.config=self.db['automod']

    @commands.Cog.listener()
    async def on_guild_channel_delete(self,channel):
        myquery = {"server-id": str(channel.guild.id)}
        mydoc = self.config.find(myquery)
        found=False
        for x in mydoc:
            found=True
        if not found:
            return
        if x["chan-del"]=="no" or x["chanlog"]=="None":
            return
        try:
            log=self.bot.get_channel(int(x["chanlog"]))
        except:
             return
        embed = discord.Embed(color=0x42d671)
        embed.set_author(name="Channel Deleted")
        embed.description=(F"Channel Name: {channel.name}")
        return await log.send(embed=embed)
    @commands.Cog.listener()
    async def on_guild_channel_create(self,channel):
        myquery = {"server-id": str(channel.guild.id)}
        mydoc = self.config.find(myquery)
        found=False
        for x in mydoc:
            found=True
        if not found:
            return
        if x["chan-create"]=="no" or x["chanlog"]=="None":
            return
        try:
            log=self.bot.get_channel(int(x["chanlog"]))
        except:
             return
        embed = discord.Embed(color=0xdd03ff)
        embed.set_author(name="Channel Created")
        embed.description=(F"Channel: {channel.mention}")
        return await log.send(embed=embed)
def setup(bot):
    bot.add_cog(ChanLog(bot))
