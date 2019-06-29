import discord 
from discord.ext import commands 
from pymongo import MongoClient  as mcl
import os 
import sys

class RoleLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = mcl(self.bot.mongodb)
        self.db = self.client['modtest']
        self.col = self.db['modlog']
        self.settings = self.db['settings']
        self.config=self.db['automod']

    @commands.Cog.listener()
    async def on_guild_role_delete(self,role):
        myquery = {"server-id": str(role.guild.id)}
        mydoc = self.config.find(myquery)
        found=False
        for x in mydoc:
            found=True
        if not found:
            return
        if x["role-del"]=="no" or x["rolelog"]=="None":
            return
        try:
            log=self.bot.get_channel(int(x["rolelog"]))
        except:
             return
        embed = discord.Embed(color=0x42d671)
        embed.set_author(name="Role Deleted")
        embed.description=(F"Role Name: {role.name}")
        return await log.send(embed=embed)
    @commands.Cog.listener()
    async def on_guild_role_create(self,role):
        myquery = {"server-id": str(role.guild.id)}
        mydoc = self.config.find(myquery)
        found=False
        for x in mydoc:
            found=True
        if not found:
            return
        if x["role-create"]=="no" or x["rolelog"]=="None":
            return
        try:
            log=self.bot.get_channel(int(x["rolelog"]))
        except:
             return
        embed = discord.Embed(color=0xdd03ff)
        embed.set_author(name="Role Created")
        embed.description=(F"Role: {role.mention}")
        return await log.send(embed=embed)
    @commands.Cog.listener()
    async def on_guild_role_update(self,before,after):
        change=False
        if before!=after:
            change=True
        if before.id!=after.id:
            change=True
        if before.name!=after.name:
            change=True
        if before.guild!=after.guild:
            change=True
        if before.colour!=after.colour:
            change=True
        if before.hoist!=after.hoist:
            change=True
        if before.managed!=after.managed:
            change=True
        if before.mentionable!=after.mentionable:
            change=True
        if before.is_default()!=after.is_default():
            change=True
        if before.members!=after.members:
            change=(True)
        if not change:
            return
        myquery = {"server-id": str(before.guild.id)}
        mydoc = self.config.find(myquery)
        found=False
        for x in mydoc:
            found=True
        if not found:
            return
        if x["role-update"]=="no" or x["rolelog"]=="None":
            return
        try:
            log=self.bot.get_channel(int(x["rolelog"]))
        except:
             return
        desc=F"Role: {before.name}\n"
        if before.name!=after.name:
            desc+=F"Old Name: {before.name}\nAfter Name: {after.name}\n"
        if before.color!=after.color:
            desc+=F"Old Color: {before.color}\nAfter Color: {after.color}\n"
        if before.position!=after.position:
            desc+=F"Old Position: {before.position}\nAfter Position: {after.position}\n"
        if before.mention!=after.mention:
            if before.mention:
                desc+=F"Before: Mentionable\nAfter: Unmentionable\n"
            else:
                desc+=F"Before: Unmentionable\nAfter: Mentionable\n"
        embed = discord.Embed(color=0xdd03ff)
        embed.set_author(name="Role Update")
        embed.description=(str(desc))
        return await log.send(embed=embed)
def setup(bot):
    bot.add_cog(RoleLog(bot))
