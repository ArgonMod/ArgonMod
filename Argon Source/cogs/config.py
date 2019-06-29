import discord 
from discord.ext import commands 
from pymongo import MongoClient  as mcl
import os 
import sys
import re
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

class Config(commands.Cog):
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
        return command + prefix
    @commands.command(name="resetconfig",asliases=["deleteconfig","configdelete"])
    @commands.has_permissions(manage_guild=True)
    async def resetconfig(self,ctx):
        found=False
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Server isn't intilized yet! You can do this wiht the `{self.bot.prefix}config` command.")
        myquery = { "server-id": str(ctx.guild.id) }
        self.config.delete_one(myquery)
        return await ctx.send(F"{self.bot.check}All your server configuration was erased! You can re-intiilize wit the `{self.bot.prefix}config` command.")
    
    @commands.group()
    @commands.has_permissions(manage_guild=True)
    async def config(self,ctx):
        if not ctx.invoked_subcommand:
            found=False
            myquery = {"server-id": str(ctx.guild.id)}
            mydoc = self.config.find(myquery)
            for x in mydoc:
              found=True
            if not found:
               #mydict = { "server-name": str(ctx.guild),"server-id": str(ctx.guild.id),"rules":[],'token-block':'no',"modlog":"None", "anti-spam":"no",
               #           "anti-invite":"no","anti-link":"no","anti-swear":"no","bad-words":['shit','fuck','niger','crap','bitch','anus'],
               #           "good-words":['can use','substitute'],"ignore":"none","msg-edit":"no","msg-del":"no","chan-create":"no","chan-del":"no","mem-join":"no",
               #           "mem-lev":"no",'msglog':'None','chanlog':'None','memlog':'None'}
               mydict = { "server-name": str(ctx.guild),"server-id": str(ctx.guild.id),"rules":[],"modlog":"None", "anti-spam":"no",
                          "anti-invite":"no","anti-link":"no","anti-swear":"no","bad-words":['shit','fuck','niger','crap','bitch','anus'],
                          "good-words":['can use','substitute'],"ignore":"none","msg-edit":"no","msg-del":"no","chan-create":"no",
                          "chan-del":"no","mem-join":"no","mem-lev":"no",'msglog':'None','chanlog':'None','memlog':'None','spam-word':'7',
                          'spam-limit':'25',"warn-mod":"no",'rolelog':'None','role-create':'no','role-del':'no','role-update':'no'}
               x = self.config.insert_one(mydict)
               return await ctx.send(F"{self.bot.check}Success! Server initilized succesfully.\nYou can now configure it with the `{self.bot.prefix}modlog`, `{self.bot.prefix}automod` or `{self.bot.prefix}autolog`command.")
            return await ctx.send(F"{self.bot.x}{ctx.author.mention}Server was intilized already! \nTo configure the server use the `{self.bot.prefix}automod` command to configure the auto mod, the `{self.bot.prefix}autolog` command to configure the autolog or the `{self.bot.prefix}modlog` command to configure the mod log.")
    @config.command(name="anti-link")
    @commands.has_permissions(manage_guild=True)
    async def antilink(self,ctx,action=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not action:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config anti-link [on/off]`.")
        alist=["on","off"]
        action=action.lower()
        if action not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config anti-link [on/off]`.")
        if action=="on":
            action="yes"
        else:
            action="no"
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "anti-link": action } }
        self.config.update_one(myquery, newvalues)
        if action=="no":
            return await ctx.send(F"{self.bot.check}Any links posted in the server will not be removed.")
        return await ctx.send(F"{self.bot.check}Any links posted in the server will be removed.")
    
    @config.command(name="anti-invite")
    @commands.has_permissions(manage_guild=True)
    async def antiinvite(self,ctx,action=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not action:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config anti-invite [on/off]`.")
        alist=["on","off"]
        action=action.lower()
        if action not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config anti-invite [on/off]`.")
        if action=="on":
            action="yes"
        else:
            action="no"
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "anti-invite": action } }
        self.config.update_one(myquery, newvalues)
        if action=="no":
            return await ctx.send(F"{self.bot.check}Any invites to discord servers posted in the server will not be removed.")
        return await ctx.send(F"{self.bot.check}Any invites to discord servers posted in the server will be removed.")
    @config.command(name="anti-swear",aliases=["antiswear"])
    @commands.has_permissions(manage_guild=True)
    async def cantiswear (self,ctx,action=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not action:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config anti-swear  [on/off]`.")
        alist=["on","off"]
        action=action.lower()
        if action not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config anti-swear  [on/off]`.")
        if action=="on":
            action="yes"
        else:
            action="no"
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "anti-swear": action } }
        self.config.update_one(myquery, newvalues)
        if action=="no":
            return await ctx.send(F"{self.bot.check}Any swear words posted in the server will not be removed.")
        return await ctx.send(F"{self.bot.check}Any swear words posted in the server will be removed. To configure this list, check out the commands in the `{self.bot.prefix}automod` list.")
    @config.group(name="badwords")
    @commands.has_permissions(manage_guild=True)
    async def badwords (self,ctx):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        blist=F"You can add a bad word with the `!config-badwords-add [word]` command.\nYou can remove a bad word with the `{self.bot.prefix}config badwords remove [word]` command.\n\n__**Current List**__\n||"
        for j in range(len(x["bad-words"])):
            blist+=(x["bad-words"])[j]+"\n"
        embed = discord.Embed(title="Current Bad Word List", description=blist+"||\n",color=self.bot.embed)
        return await ctx.send(embed=embed)
    @badwords.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def addbadword (self,ctx,word=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not word:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config badwords add [word]`")
        if str(word) in (x["bad-words"]):
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} This word is already listed as a bad word.`")
        oldList=x["bad-words"]
        oldList.append(word)
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "bad-words": oldList } }
        self.config.update_one(myquery, newvalues)
        return await ctx.send(F"{self.bot.check} ||{word}|| has been added to the bad word list.")

    @badwords.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def removebadword (self,ctx,word=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not word:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config badwords add [word]`")
        if str(word) not in (x["bad-words"]):
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} This word is not listed as a bad word.`")
        oldList=x["bad-words"]
        spot=oldList.index(word)
        oldList.pop(spot)
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "bad-words": oldList } }
        self.config.update_one(myquery, newvalues)
        return await ctx.send(F"{self.bot.check} ||{word}|| has been removed from the bad word list.")

    #@config.group(name="goodwords")
    @commands.has_permissions(manage_guild=True)
    async def goodwords (self,ctx):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        blist="You can add a good word with the `{self.bot.prefix}config goodwords add [word]` command.\nYou can remove a good word with the `{self.bot.prefix}config goodwords remove [word]` command.\n\n__**Current List**__\n"
        for j in range(len(x["good-words"])):
            blist+=(x["good-words"])[j]+"\n"
        embed = discord.Embed(title="Current Good Word List", description=blist,color=self.bot.embed)
        return await ctx.send(embed=embed)
    #@goodwords.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def addgoodword (self,ctx,word=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not word:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config goodwords add [word]`")
        if str(word) in (x["good-words"]):
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} This word is already listed as a good word.`")
        oldList=x["good-words"]
        oldList.append(word)
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "good-words": oldList } }
        self.config.update_one(myquery, newvalues)
        return await ctx.send(F"{self.bot.check} {word} has been added to the good word list.")

    #@goodwords.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def removegoodword (self,ctx,word=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not word:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config goodwords add [word]`")
        if str(word) not in (x["good-words"]):
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} This word is not listed as a bad word.`")
        oldList=x["good-words"]
        spot=oldList.index(word)
        oldList.pop(spot)
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "good-words": oldList } }
        self.config.update_one(myquery, newvalues)
        return await ctx.send(F"{self.bot.check} {word} has been removed from the good word list.")
    @commands.group(name="goodwords")
    @commands.has_permissions(manage_guild=True)
    async def goodwords (self,ctx):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `!config` command.")
        blist="You can add a good word with the `!config-goodwords-add [word]` command.\nYou can remove a good word with the `!config-goodwords-remove [word]` command.\n\n__**Current List**__\n"
        for j in range(len(x["good-words"])):
            blist+=(x["good-words"])[j]+"\n"
        embed = discord.Embed(title="Current Good Word List", description=blist,color=self.bot.embed)
        return await ctx.send(embed=embed)
    @goodwords.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def addgoodword (self,ctx,word=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `!config` command.")
        if not word:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `!config-goodwords-add [word]`")
        if str(word) in (x["good-words"]):
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} This word is already listed as a good word.`")
        oldList=x["good-words"]
        oldList.append(word)
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "good-words": oldList } }
        self.config.update_one(myquery, newvalues)
        return await ctx.send(F"{self.bot.check} {word} has been added to the good word list.")

    @goodwords.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def removegoodword (self,ctx,word=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `!config` command.")
        if not word:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `!config-goodwords-add [word]`")
        if str(word) not in (x["good-words"]):
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} This word is not listed as a bad word.`")
        oldList=x["good-words"]
        spot=oldList.index(word)
        oldList.pop(spot)
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "good-words": oldList } }
        self.config.update_one(myquery, newvalues)
        return await ctx.send(F"{self.bot.check} {word} has been removed from the good word list.")
    
    @config.command(name="ignore")
    @commands.has_permissions(manage_guild=True)
    async def ignore (self,ctx,role:discord.Role=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not role:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config ignore [@role]`")
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "ignore": role.id } }
        self.config.update_one(myquery, newvalues)
        return await ctx.send(F"{self.bot.check} {role.name} is the new ignore role. Anyone with this role can bypass the automod.")
    @config.command(name="modchan")
    @commands.has_permissions(manage_guild=True)
    async def channel (self,ctx,chan:discord.TextChannel=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not chan:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config modlog [#channel]`")
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "modlog": chan.id } }
        self.config.update_one(myquery, newvalues)
        return await ctx.send(F"{self.bot.check} {chan.name} is the new automod channel.")
    @commands.command(name="autorule",aliases=["auto-rule","autorules","rulelist"])
    @commands.has_permissions(manage_guild=True)
    async def autorule (self,ctx):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        found=False
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        rlist=F"You can add a rule with the `{self.bot.prefix}addrule` command and remove a rule with the `{self.bot.prefix}removerule` command.\n"
        rlists=x["rules"]
        for j in range(len(rlists)):
            rules=rlists[j]
            if rules[1]!="tempmute":
                rlist+=F"**{j+1}.** After {rules[0]} warnings kick user.\n"
            else:
                rlist+=F"**{j+1}.** After {rules[0]} warnings mute user for {rules[3]}.\n"
        if rlist=="":
            rlist=F"No Auto Rules set. You can set one with the `{self.bot.prefix}addrule` command."
        embed = discord.Embed(title="Current Auto Rule List", description=rlist,color=self.bot.embed)
        return await ctx.send(embed=embed)
    @commands.command(name="remove-rule",aliases=["removerule"])
    @commands.has_permissions(manage_guild=True)
    async def remrule (self,ctx,warnings=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        found=False
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if warnings==None:
            return await ctx.send(F'To remove a rule, do the following, post\n `{self.bot.prefix}removerule[number of rule to delete]`\nTo get a list of rules that can be deleated, use the `{self.bot.prefix}autorule` command.')
        if not warnings.isdigit():
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}removerule[number of rule to delete]`.")
        rlist=x["rules"]
        if (int(warnings))>len(rlist):
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}removerule[number of rule to delete]`.")
        await ctx.send(F"{self.bot.check} Rule removed!")
        rlist.pop(int(warnings)-1)
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "rules": rlist } }
        self.config.update_one(myquery, newvalues)
        
    @commands.command(name="add-rule",aliases=["addrule"], description="Add a limit to the warnings so if they hit that limit they get a punishment.")
    @commands.has_permissions(manage_guild=True)
    async def addrule (self,ctx,warnings=None,action=None, lmt: typing.Optional[convtime] = None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        found=False
        if not lmt:
            lmt = 3600
        time1 = lmt
        days = time1 // (24 * 3600)
        time1 - time1 % (24 * 3600)
        hours = time1 // 3600 
        time1 %= 3600
        minutes = time1 // 60
        time1 %= 60
        seconds = time1 
        server = ctx.guild
        time_str = " ".join((f'{y} {x}' for x,y in vars().items() if x in ('days','hours','minutes','seconds') if y > 0))
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if warnings==None:
            return await ctx.send(F'''To remove a rule, do the following, post\n `{self.bot.prefix}addrule[amount of warnings required to triger this rule][tempmute/kick/ban/permmute] [if mute, for how long in minutes]`\n\nAn example is `{self.bot.prefix}addrule 5 mute 10` which would mute someone for 10 minutes if they reached 5 warnings.\nAnother example is `{self.bot.prefix}addrule 10 kick` which would kick someone if they reached 10 warnings.''')
        if not warnings.isdigit():
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}removerule[number of rule to remove]tempmute/kick/ban/permmute] [if mute, for how long in minutes]`. \nFor more information use the `{self.bot.prefix}addrule` command.")
        try:
            action=action.lower()
        except:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}addrule[amount of warnings required to triger this rule][tempmute/kick/ban/permmute] [if mute, for how long in minutes]`. \nFor more information use the `{self.bot.prefix}addrule` command.")
        
        if action.lower()=='mute' and not time.isdigit():
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}addrule[amount of warnings required to triger this rule][tempmute/kick/ban/permmute] [if tempmute, for how long in minutes]`. \nFor more information use the `{self.bot.prefix}addrule` command.")
        alist=['tempmute','kick','ban','permmute']
        if action.lower() not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}addrule[amount of warnings required to triger this rule][tempmute/kick/ban/permmute] [if tempmute, for how long in minutes]`. \nFor more information use the `{self.bot.prefix}addrule` command.")
        rlist=x["rules"]
        
        if action=="tempmute":
            rlist.append([warnings,action,time1,time_str])
        elif action=="permmute":
            rlist.append([warnings,"pmute"])
        else:
            rlist.append([warnings,action])
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "rules": rlist } }
        self.config.update_one(myquery, newvalues)
        if action!="tempmute":
            return await ctx.send(F"{self.bot.check} When a user get {warnings} warnings, they will be {action}ed.")
        return await ctx.send(F"{self.bot.check} When a user get {warnings} warnings, they will be muted for {time_str}.")

    
    @config.command(name="msglog")
    @commands.has_permissions(manage_guild=True)
    async def msglog (self,ctx,chan:discord.TextChannel=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not chan:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config msglog [#channel]`")
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "msglog": chan.id } }
        self.config.update_one(myquery, newvalues)
        return await ctx.send(F"{self.bot.check} {chan.name} is the new message logs channel.")
    @config.command(name="msg-edit")
    @commands.has_permissions(manage_guild=True)
    async def msgedit(self,ctx,action=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not action:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config msg-edit [on/off]`.")
        alist=["on","off"]
        action=action.lower()
        if action not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config msg-edit [on/off]`.")
        if action=="on":
            action="yes"
        else:
            action="no"
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "msg-edit": action } }
        self.config.update_one(myquery, newvalues)
        if action=="no":
            return await ctx.send(F"{self.bot.check}Any edited messages will not be logged.")
        return await ctx.send(F"{self.bot.check}Any edited messages will be logged.")
    @config.command(name="msg-del")
    @commands.has_permissions(manage_guild=True)
    async def msgdel(self,ctx,action=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not action:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config msg-del [on/off]`.")
        alist=["on","off"]
        action=action.lower()
        if action not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config msg-del [on/off]`.")
        if action=="on":
            action="yes"
        else:
            action="no"
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "msg-del": action } }
        self.config.update_one(myquery, newvalues)
        if action=="no":
            return await ctx.send(F"{self.bot.check}Any deleated messages will not be logged.")
        return await ctx.send(F"{self.bot.check}Any deleated messages will be logged.")
    @config.command(name="chanlog")
    @commands.has_permissions(manage_guild=True)
    async def chanlog (self,ctx,chan:discord.TextChannel=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not chan:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config chanlog [#channel]`")
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "chanlog": chan.id } }
        self.config.update_one(myquery, newvalues)
        return await ctx.send(F"{self.bot.check} {chan.name} is the new channel logs channel.")
    @config.command(name="chan-create")
    @commands.has_permissions(manage_guild=True)
    async def chancrea(self,ctx,action=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not action:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config chan-create [on/off]`.")
        alist=["on","off"]
        action=action.lower()
        if action not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config chan-create [on/off]`.")
        if action=="on":
            action="yes"
        else:
            action="no"
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "chan-create": action } }
        self.config.update_one(myquery, newvalues)
        if action=="no":
            return await ctx.send(F"{self.bot.check}Any created channels will not be logged.")
        return await ctx.send(F"{self.bot.check}Any created channels will be logged.")
    @config.command(name="chan-del")
    @commands.has_permissions(manage_guild=True)
    async def chandel(self,ctx,action=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not action:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config chan-del [on/off]`.")
        alist=["on","off"]
        action=action.lower()
        if action not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config chan-del [on/off]`.")
        if action=="on":
            action="yes"
        else:
            action="no"
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "chan-del": action } }
        self.config.update_one(myquery, newvalues)
        if action=="no":
            return await ctx.send(F"{self.bot.check}Any deleted channels will not be logged.")
        return await ctx.send(F"{self.bot.check}Any deleted channels will be logged.")
    @config.command(name="memlog")
    @commands.has_permissions(manage_guild=True)
    async def memlog (self,ctx,chan:discord.TextChannel=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not chan:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config memlog [#channel]`")
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "memlog": chan.id } }
        self.config.update_one(myquery, newvalues)
        return await ctx.send(F"{self.bot.check} {chan.name} is the new member logs channel.")
    @config.command(name="member-join")
    @commands.has_permissions(manage_guild=True)
    async def memjoin(self,ctx,action=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not action:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config mem-join [on/off]`.")
        alist=["on","off"]
        action=action.lower()
        if action not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config mem-join [on/off]`.")
        if action=="on":
            action="yes"
        else:
            action="no"
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "mem-join": action } }
        self.config.update_one(myquery, newvalues)
        if action=="no":
            return await ctx.send(F"{self.bot.check}Any new members will not be logged.")
        return await ctx.send(F"{self.bot.check}Any new members will be logged.")
    @config.command(name="member-leave")
    @commands.has_permissions(manage_guild=True)
    async def memleave(self,ctx,action=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not action:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config mem-leave  [on/off]`.")
        alist=["on","off"]
        action=action.lower()
        if action not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config mem-leave  [on/off]`.")
        if action=="on":
            action="yes"
        else:
            action="no"
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "mem-lev": action } }
        self.config.update_one(myquery, newvalues)
        if action=="no":
            return await ctx.send(F"{self.bot.check}Any members leaving will not be logged.")
        return await ctx.send(F"{self.bot.check}Any members leaving will be logged.")
    @config.command(name="rolelog")
    @commands.has_permissions(manage_guild=True)
    async def rolelog (self,ctx,chan:discord.TextChannel=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not chan:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config rolelog [#channel]`")
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "rolelog": chan.id } }
        self.config.update_one(myquery, newvalues)
        return await ctx.send(F"{self.bot.check} {chan.name} is the new role logs channel.")
    @config.command(name="role-create")
    @commands.has_permissions(manage_guild=True)
    async def rolecreate(self,ctx,action=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not action:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config role-create  [on/off]`.")
        alist=["on","off"]
        action=action.lower()
        if action not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config role-create  [on/off]`.")
        if action=="on":
            action="yes"
        else:
            action="no"
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "role-create": action } }
        self.config.update_one(myquery, newvalues)
        if action=="no":
            return await ctx.send(F"{self.bot.check}Any created roles will not be logged.")
        return await ctx.send(F"{self.bot.check}Any created roles will be logged.")
    @config.command(name="role-deleate",aliases=["role-del"])
    @commands.has_permissions(manage_guild=True)
    async def roledel(self,ctx,action=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not action:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config role-del  [on/off]`.")
        alist=["on","off"]
        action=action.lower()
        if action not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config role-del  [on/off]`.")
        if action=="on":
            action="yes"
        else:
            action="no"
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "role-del": action } }
        self.config.update_one(myquery, newvalues)
        if action=="no":
            return await ctx.send(F"{self.bot.check}Any deleated roles will not be logged.")
        return await ctx.send(F"{self.bot.check}Any deleated roles will be logged.")
    @config.command(name="role-update",aliases=["role-updated"])
    @commands.has_permissions(manage_guild=True)
    async def roleupdate(self,ctx,action=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not action:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config role-update  [on/off]`.")
        alist=["on","off"]
        action=action.lower()
        if action not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config role-update  [on/off]`.")
        if action=="on":
            action="yes"
        else:
            action="no"
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "role-update": action } }
        self.config.update_one(myquery, newvalues)
        if action=="no":
            return await ctx.send(F"{self.bot.check}Any updated roles will not be logged.")
        return await ctx.send(F"{self.bot.check}Any updated roles will be logged.")
    @config.command(name="modwarn")
    @commands.has_permissions(manage_guild=True)
    async def modwarn(self,ctx,action=None):
        myquery = {"server-id": str(ctx.guild.id)}
        mydoc = self.config.find(myquery)
        for x in mydoc:
          found=True
        if not found:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Please initilize the server with the `{self.bot.prefix}config` command.")
        if not action:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config modwarn [on/off]`.")
        alist=["on","off"]
        action=action.lower()
        if action not in alist:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The correct usage of this command is `{self.bot.prefix}config modwarn [on/off]`.")
        if action=="on":
            action="yes"
        else:
            action="no"
        myquery = {"server-id": str(ctx.guild.id)}
        newvalues = { "$set": { "warn-mod": action } }
        self.config.update_one(myquery, newvalues)
        if action=="no":
            return await ctx.send(F"{self.bot.check}Any automod infractions will not count as warnings.")
        return await ctx.send(F"{self.bot.check}Any automod infractions will count as warnings.")
def setup(bot):
    bot.add_cog(Config(bot))
