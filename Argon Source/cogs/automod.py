import discord 
from discord.ext import commands 
from pymongo import MongoClient  as mcl
import os 
import sys
from datetime import datetime
import re

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


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.client = mcl(self.bot.mongodb)
        self.db = self.client['modtest']
        self.col = self.db['modlog']
        self.settings = self.db['settings']
        self.config=self.db['automod']

    def prefixfy(self, input):
        number = str(input)
        num = len(number) - 2
        num2 = len(number) - 1
        if int(number[num:]) < 11 or int(number[num:]) > 13:
            if int(number[num2:]) == 1:
                prefix = "st"
            elif int(number[num2:]) == 2:
                prefix = "nd"
            elif int(number[num2:]) == 3:
                prefix = "rd"
            else:
                prefix = "th"
        else:
            prefix = "th"
        return number + prefix

              
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def automod(self,ctx):
        chan1="DISABLED"
        chan2=self.bot.disabled
        chan3="None"
        link1="DISABLED"
        link2=self.bot.disabled
        invite1="DISABLED"
        invite2=self.bot.disabled
        spam1="DISABLED"
        spam2=self.bot.disabled
        badwords=""
        goodwords=""
        ignore1="DISABLED"
        ignore2=self.bot.disabled
        ignore3="None"
        warnmod1="DISABLED"
        warnmod2=self.bot.disabled
        found=False
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"Please use the `{self.bot.prefix}config` command to get started.")
        if x["modlog"]!="None":
            chan1="ENABLED"
            chan2=self.bot.enabled
            try:
                chan3=self.bot.get_channel(int(x["modlog"])).mention
            except:
                chan3="Channel Was Deleated"
        if x["anti-spam"]=="yes":
            spam1="ENABLED"
            spam2=self.bot.enabled
        if x["anti-invite"]=="yes":
            invite1="ENABLED"
            invite2=self.bot.enabled
        if x["anti-link"]=="yes":
            link1="ENABLED"
            link2=self.bot.enabled
        if x["warn-mod"]=="yes":
            warnmod1="ENABLED"
            warnmod2=self.bot.enabled
        if x["ignore"]!="none":
            ignore1="ENABLED"
            ignore2=self.bot.enabled
            try:
                ignore3=ctx.guild.get_role(int(x["ignore"])).mention
            except:
                ignore3="Role Was Deleated"
        if x["bad-words"]!="":
            for x in (badwords):
                badwords+=x+"\n"
        else:
            badwords=str(self.bot.enabled)+"Anti-Swear Disabled"
            
        #if x["good-words"]!="":
        #    for x in (goodwords):
        #        goodwords+=x+"\n"
        #else:
        #    goodwords=str(self.bot.enabled)+"Anti-Swear Disabled"
         
        embed = discord.Embed(color=self.bot.embed)
        embed.set_author(name="AutoMod Configurations")
        embed.add_field(name=f"{self.bot.prefix}config modchan [#channel]", value=f"""
        This will set a channel for all the automod logs to be sent to.
        Current: {chan2} **{chan1}**
        Current Channel: {chan3}
        """)
        embed.add_field(name=f"{self.bot.prefix}config anti-link [on/off]", value=f"""
        This will prevent links from being posted in server.
        Current: {link2} **{link1}**
        """)
        embed.add_field(name=f"{self.bot.prefix}config anti-invite [on/off]", value=f"""
        This will prevent links from being posted in server.
        Current: {invite2} **{invite1}**
        """)
        embed.add_field(name=f"{self.bot.prefix}antispam", value=f"""
        Opens up settings to config anti-swear.
        Current: {spam2} **{spam1}**
        """)
        embed.add_field(name=f"{self.bot.prefix}antiswear", value=f"""
        Opens up settings to config anti-swear.
        """)
        embed.add_field(name=f"{self.bot.prefix}config ignore [@role]", value=f"""
        The role which doesn't get the anti-spam,invite,swear and spam filter applied to it.
        Current: {ignore2} **{ignore1}**
        Role: {ignore3}
        """,inline=False)
        embed.add_field(name=f"{self.bot.prefix}autorule ", value=f"""
        Configure the automute systems.
        """,inline=False) 
        await ctx.send(embed=embed)
        
    @commands.group(name="anti-swear",aliases=["antiswear"])
    @commands.has_permissions(manage_guild=True)
    async def swearmod(self,ctx):
        swear1="DISABLED"
        swear2=self.bot.disabled
        badwords=""
        goodwords=""
        
        found=False
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send("Please use the `!config` command to get started.")
        if x["anti-swear"]=="yes":
            swear1="ENABLED"
            swear2=self.bot.enabled
        embed = discord.Embed(color=self.bot.embed)
        embed.set_author(name="Anti Swear Configurations")
        embed.add_field(name=f"{self.bot.prefix}config anti-swear [on/off]", value=f"""
        This will prevent swear words from being posted in server.
        Current: {swear2} **{swear1}**
        """)
        embed.add_field(name=f"{self.bot.prefix}config badwords", value=f"""
        Shows current list of badwords.
        """,inline=False)
        embed.add_field(name=f"{self.bot.prefix}config badwords-add [word]", value=f"""
        Adds a bad word to the list.
        """,inline=True)
        embed.add_field(name=f"{self.bot.prefix}config badwords-remove [word]", value=f"""
        Removes a bad word to the list.
        """,inline=True)
        embed.add_field(name=f"{self.bot.prefix}config goodwords", value=f"""
        Shows current list of goodwords.
        """,inline=False)
        embed.add_field(name=f"{self.bot.prefix}config goodwords-add [word]", value=f"""
        Adds a bad word to the list.
        """,inline=True)
        embed.add_field(name=f"{self.bot.prefix}config goodwords-remove [word]", value=f"""
        Removes a good word to the list.
        """,inline=True)
        await ctx.send(embed=embed)
    @commands.command()
    async def ping(self, ctx):
        '''Shows the latency of me. Usage: !ping'''
        current = ctx.message.edited_at.timestamp() if ctx.message.edited_at else ctx.message.created_at.timestamp()
        embed=discord.Embed(title="Pinging")
        message = await ctx.send(embed=embed)
        embed=discord.Embed(description=f"""
        :stopwatch: {round((datetime.utcnow().timestamp() - current)*1000)}ms
        :heartbeat: {round(self.bot.latencies[ctx.guild.shard_id][1]*1000)}ms
        (Shard {ctx.guild.shard_id + 1})
        """)
        await message.edit(embed=embed)
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self,ctx,amount=None):
        if not amount:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The proper usage of this command is `{self.bot.prefix}slowmode [change slowmode to]`.")
        time=convtime(amount)
        time=int(time)
        await ctx.channel.edit(slowmode_delay=time)
        await ctx.send(F"{self.bot.check} Success! Slowmode time changed to {time} seconds.")
def setup(bot):
    bot.add_cog(AutoMod(bot))
