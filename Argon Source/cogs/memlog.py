import discord 
from discord.ext import commands 
from pymongo import MongoClient  as mcl
import os 
import sys

class MemLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = mcl(self.bot.mongodb)
        self.db = self.client['modtest']
        self.col = self.db['modlog']
        self.settings = self.db['settings']
        self.config=self.db['automod']
        self.invites=self.db['invites']

    @commands.Cog.listener()
    async def on_member_join(self,member):
        invites=await member.guild.invites()
        ilist=[]
        for invite in invites:
            ilist.append([invite.code,invite.uses])
        found=False
        myquery = {"server-id": str(member.guild.id)}
        mydoc = self.invites.find(myquery)
        for x in mydoc:
            found=True
        
        if not found:
            mydict = { "server-id": str(member.guild.id), "server-name": str(member.guild.name),"invites":ilist}
            self.invites.insert_one(mydict)
            inviteused="None Found."
        else:
            inviteused="Unable To Locate"
            creator="Unable To Locate."
            myquery = { "server-id": str(member.guild.id) }
            newvalues = { "$set": { "invites": ilist } }
            self.invites.update_one(myquery, newvalues)
            olist=x["invites"]
            for invite in (olist):
                for invite2 in ilist:
                    if invite[0]==invite2[0]:
                        item2=await member.guild.invites()
                        for invite12 in item2:
                            if invite12.code==invite2[0]:
                                item=invite12

                        if invite[1]!=item.uses:
                            inviteused=await self.bot.fetch_invite(invite[0])
                            creator=item.inviter
        myquery = {"server-id": str(member.guild.id)}
        mydoc = self.config.find(myquery)
        found=False
        for x in mydoc:
            found=True
        if not found:
            return
        if x["mem-join"]=="no" or x["chanlog"]=="None":
            return
        try:
            log=self.bot.get_channel(int(x["chanlog"]))
        except:
             return
        joined_discord = member.created_at.strftime("%d %b %Y %H:%M")
        embed = discord.Embed(color=0x2bb0e0)
        embed.set_author(name="Member Joined Server")
        embed.add_field(name="Member Name:",value=member.name)
        embed.add_field(name="Member ID:",value=member.id)
        embed.add_field(name="Joined Discord:",value=joined_discord)
        embed.add_field(name="Used Invite:",value=inviteused)
        embed.add_field(name="Invite Made By:",value=creator)
        embed.add_field(name="Join Position:",value=member.guild.member_count)
        return await log.send(embed=embed)
    @commands.Cog.listener()
    async def on_member_remove(self,member):
        invites=await member.guild.invites()
        ilist=[]
        for invite in invites:
            ilist.append([invite.code,invite.uses])
        found=False
        myquery = {"server-id": str(member.guild.id)}
        mydoc = self.invites.find(myquery)
        for x in mydoc:
            found=True
        if found:
            myquery = { "server-id": str(member.guild.id) }
            newvalues = { "$set": { "invites": ilist } }
            self.invites.update_one(myquery, newvalues)
        else:
            mydict = { "server-id": str(member.guild.id), "server-name": str(member.guild.name),"invites":[]}
            self.invites.insert_one(mydict)
        myquery = {"server-id": str(member.guild.id)}
        mydoc = self.config.find(myquery)
        found=False
        for x in mydoc:
            found=True
        if not found:
            return
        if x["mem-lev"]=="no" or x["chanlog"]=="None":
            return
        try:
            log=self.bot.get_channel(int(x["chanlog"]))
        except:
             return
        joined_discord = member.created_at.strftime("%d %b %Y %H:%M")
        joined_server = member.joined_at.strftime("%d %b %Y %H:%M")
        embed = discord.Embed(color=0xe62c07)
        embed.set_author(name="Member Left Server")
        embed.add_field(name="Member Name:",value=member.name)
        embed.add_field(name="Member ID:",value=member.id)
        embed.add_field(name="Joined Discord:",value=joined_discord)
        embed.add_field(name="Joined Server:",value=joined_server)
        return await log.send(embed=embed)
def setup(bot):
    bot.add_cog(MemLog(bot))
