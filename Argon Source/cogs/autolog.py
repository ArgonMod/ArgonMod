import discord 
from discord.ext import commands 
from pymongo import MongoClient  as mcl
import os 
import sys
 
class AutoLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = mcl(self.bot.mongodb)
        self.db = self.client['modtest']
        self.col = self.db['modlog']
        self.settings = self.db['settings']
        self.config=self.db['automod']

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def autolog(self,ctx):
        msglog1="DISABLED"
        msglog2=self.bot.disabled
        msglog3="None"
        msge1="DISABLED"
        msge2=self.bot.disabled
        msgd1="DISABLED"
        msgd2=self.bot.disabled
        chanlog1="DISABLED"
        chanlog2=self.bot.disabled
        chanlog3="None"
        chanc1="DISABLED"
        chanc2=self.bot.disabled
        chand1="DISABLED"
        chand2=self.bot.disabled
        memlog1="DISABLED"
        memlog2=self.bot.disabled
        memlog3="None"
        memj1="DISABLED"
        memj2=self.bot.disabled
        meml1="DISABLED"
        meml2=self.bot.disabled
        rolelog1="DISABLED"
        rolelog2=self.bot.disabled
        rolelog3="None"
        rolec1="DISABLED"
        rolec2=self.bot.disabled
        roled1="DISABLED"
        roled2=self.bot.disabled
        roleu1="DISABLED"
        roleu2=self.bot.disabled
        found=False
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"Please use the `{self.bot.prefix}config` command to get started.")
        if x["msglog"]!="None":
            msglog1="ENABLED"
            msglog2=self.bot.enabled
            try:
                msglog3=self.bot.get_channel(int(x["msglog"])).mention
            except:
                msglog3="Channel Was Deleated"
        if x["chanlog"]!="None":
            chanlog1="ENABLED"
            chanlog2=self.bot.enabled
            try:
                chanlog3=self.bot.get_channel(int(x["chanlog"])).mention
            except:
                chanlog3="Channel Was Deleated"
        if x["memlog"]!="None":
            memlog1="ENABLED"
            memlog2=self.bot.enabled
            try:
                memlog3=self.bot.get_channel(int(x["memlog"])).mention
            except:
                memlog3="Channel Was Deleated"
        if x["rolelog"]!="None":
            rolelog1="ENABLED"
            rolelog2=self.bot.enabled
            try:
                rolelog3=self.bot.get_channel(int(x["rolelog"])).mention
            except:
                rolelog3="Channel Was Deleated"
        if x["msg-edit"]=="yes":
            msge1="ENABLED"
            msge2=self.bot.enabled
        if x["msg-del"]=="yes":
            msgd1="ENABLED"
            msgd2=self.bot.enabled
        if x["chan-create"]=="yes":
            chanc1="ENABLED"
            chanc2=self.bot.enabled
        if x["chan-del"]=="yes":
            chand1="ENABLED"
            chand2=self.bot.enabled
        if x["mem-join"]=="yes":
            memj1="ENABLED"
            memj2=self.bot.enabled
        if x["mem-lev"]=="yes":
            meml1="ENABLED"
            meml2=self.bot.enabled
        if x["role-create"]=="yes":
            rolec1="ENABLED"
            rolec2=self.bot.enabled
        if x["role-del"]=="yes":
            roled1="ENABLED"
            roled2=self.bot.enabled
        if x["role-update"]=="yes":
            roleu1="ENABLED"
            roleu2=self.bot.enabled
        embed = discord.Embed(color=self.bot.embed)
        embed.set_author(name="AutLog Configurations")
        embed.add_field(name=f"{self.bot.prefix}config msglog [#channel]", value=f"""
        This will set a channel for all the message event logs.
        Current: {msglog2} **{msglog1}**
        Current Channel: {msglog3}
        """)
        embed.add_field(name=f"{self.bot.prefix}config msg-edit [on/off]", value=f"""
        This will log whenever a message is edited.
        Current: {msge2} **{msge1}**
        """)
        embed.add_field(name=f"{self.bot.prefix}config msg-del [on/off]", value=f"""
        This will log whenever a message is deleated.
        Current: {msgd2} **{msgd1}**
        """)
        embed.add_field(name=f"{self.bot.prefix}config chanlog [#channel]", value=f"""
        This will set a channel for all the message event logs.
        Current: {chanlog2} **{chanlog1}**
        Current Channel: {chanlog3}
        """)
        embed.add_field(name=f"{self.bot.prefix}config chan-create [on/off]", value=f"""
        This will log whenever a channel is created.
        Current: {chanc2} **{chanc1}**
        """,inline=False)
        embed.add_field(name=f"{self.bot.prefix}config chan-del [on/off]", value=f"""
        This will log whenever a channel is deleated.
        Current: {chand2} **{chand1}**
        """,inline=False)
        embed.add_field(name=f"{self.bot.prefix}config memlog [#channel]", value=f"""
        This will set a channel for all the message event logs.
        Current: {memlog2} **{memlog1}**
        Current Channel: {memlog3}
        """)
        embed.add_field(name=f"{self.bot.prefix}config member-join [on/off]", value=f"""
        This will log when a member joins.
        Current: {memj2} **{memj1}**
        """,inline=False)
        embed.add_field(name=f"{self.bot.prefix}config member-leave [on/off]", value=f"""
        This will log when a member leaves.
        Current: {meml2} **{meml1}**
        """,inline=False)
        embed.add_field(name=f"{self.bot.prefix}config rolelog [#channel]", value=f"""
        This will set a channel for all the role event logs.
        Current: {rolelog2} **{rolelog1}**
        Current Channel: {rolelog3}
        """)
        embed.add_field(name=f"{self.bot.prefix}config role-create [on/off]", value=f"""
        This will log when a role is created.
        Current: {rolec2} **{rolec1}**
        """,inline=False)
        embed.add_field(name=f"{self.bot.prefix}config role-del [on/off]", value=f"""
        This will log when a role is deleated.
        Current: {roled2} **{roled1}**
        """,inline=False)
        embed.add_field(name=f"{self.bot.prefix}config role-update [on/off]", value=f"""
        This will log when a role is updated.
        Current: {roleu2} **{roleu1}**
        """,inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(AutoLog(bot))
