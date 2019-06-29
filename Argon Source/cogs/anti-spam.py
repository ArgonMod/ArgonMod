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
        self.data = self.col.find_one()
 
  

    async def send_log(self, server, action,user, reason, duration = None, days = None):
        
        self.data = self.col.find_one()
        if not str(server.id) in self.data:          
            if action == "Mute" or action=="Tempban":
                case = {}
                case['id'] = 1 
                case['user'] = str(user.id)
                case['mod'] = str(self.bot.user.id)
                case['action'] = action
                case['time'] = time.strftime('%d-%m-%Y')
                case['reason'] = reason
                case['duration'] = duration
                document = {"$set": {str(server.id):{
                    "channel": "not set",
                    "status": "disabled",
                    "case#": 1,
                    "cases": [case],
                }}}
                self.col.update_one({"auth": True}, document)
            case = {}
            case['id'] = 1 
            case['user'] = str(user.id)
            case['mod'] = str(self.bot.user.id)
            case['action'] = action
            case['time'] = time.strftime('%d-%m-%Y')
            case['reason'] = reason 

            document = {"$set": {str(server.id):{
                "channel": "not set",
                "status": "disabled",
                "case#": 1,
                "cases": [case],
            }}}
            self.col.update_one({"auth": True}, document)
        mod_chan = server.get_channel(int(self.data[str(server.id)]['channel']))
        if not mod_chan:
            if action == "Mute" or action == "Tempban":
                case = {}
                case['id'] = self.data[str(server.id)]['case#'] + 1 
                case['user'] = str(user.id)
                case['mod'] = str(self.bot.user.id)
                case['action'] = action
                case['time'] = time.strftime('%d-%m-%Y')
                case['reason'] = reason 
                case['duration'] = duration
                document = {"$set": {str(server.id):{
                    "channel": self.data[str(server.id)]['channel'],
                    "status": self.data[str(server.id)]['status'],
                    "case#": self.data[str(server.id)]['case#'] + 1,
                    "cases": self.data[str(server.id)]['cases'] + [case]
                }}}
                self.col.update_one({"auth": True}, document)
            else:
                case = {}
                case['id'] = self.data[str(server.id)]['case#'] + 1
                case['user'] = str(user.id)
                case['mod'] = str(self.bot.user.id)
                case['action'] = action
                case['time'] = time.strftime('%d-%m-%Y')
                case['reason'] = reason 
                document = {"$set": {str(server.id):{
                    "channel": self.data[str(server.id)]['channel'],
                    "status": self.data[str(server.id)]['status'],
                    "case#": self.data[str(server.id)]['case#'] + 1,
                    "cases": self.data[str(server.id)]['cases'] + [case]
                }}}
                self.col.update_one({"auth": True}, document)
            return
        if self.data[str(server.id)]["status"] == "disabled":
            case1 = self.data[str(server.id)]['case#']
            if action == "Mute" or action == "Tempban":
                case = {}
                case['id'] = case1 + 1
                case['user'] = str(user.id)
                case['mod'] = str(self.bot.user.id)
                case['action'] = action
                case['time'] = time.strftime('%d-%m-%Y')
                case['reason'] = reason 
                case['duration'] = duration
                document = {"$set": {str(server.id):{
                    "channel": self.data[str(server.id)]['channel'],
                    "status": self.data[str(server.id)]['status'],
                    "case#": self.data[str(server.id)]['case#'] + 1,
                    "cases": self.data[str(server.id)]['cases'] + [case]
                }}}
                self.col.update_one({"auth": True}, document)
            else:
                case = {}
                case['id'] = case1  + 1
                case['user'] = str(user.id)
                case['mod'] = str(self.bot.user.id)
                case['action'] = action
                case['time'] = time.strftime('%d-%m-%Y')
                case['reason'] = reason 
                document = {"$set": {str(server.id):{
                    "channel": self.data[str(server.id)]['channel'],
                    "status": self.data[str(server.id)]['status'],
                    "case#": self.data[str(server.id)]['case#'] + 1,
                    "cases": self.data[str(server.id)]['cases'] + [case]
                }}}
                self.col.update_one({"auth": True}, document)
            return
        color = self.bot.embed
        if action == "Warn":
            color = 0xEDF562
        if action == "Mute":
            color = 0x62ABF5
        if action == "Ban":
            color = 0xF56264
        if action == "Kick":
            color = 0xFFA200
        if action == "Unmute":
            color = 0x36FFBC
        if action == "Unban": 
            color = 0x36FFBC
        if action == "Softban": 
            color = 0xFFA200
        if action == "Tempban":
            color = 0xFF36FF
        if action == "Pmute":
            color = 0x367CFF
        else:
            case1 = self.data[str(server.id)]['case#']
            mod = self.bot.user
            if action == "Mute" or action == "Tempban":
                embed = discord.Embed(color=color, timestamp=datetime.utcnow())
                embed.set_author(name="{} | Case {:,}".format(action, self.data[str(server.id)]['case#']+1))
                embed.add_field(name=f"User", value=f"{user} ({user.mention})")
                embed.add_field(name=f"Moderator", value=f"{mod} ({mod.mention})")
                embed.add_field(name=f"Duration", value=duration)
                embed.add_field(name=f"Reason", value=reason,inline=False)
                embed.set_footer(text=f"ID: {user.id}")
                msg = await mod_chan.send(embed=embed)
                case = {}
                case['id'] = case1 + 1
                case['user'] = str(user.id)
                case['mod'] = str(self.bot.user.id)
                case['time'] = time.strftime('%d-%m-%Y')
                case['reason'] = reason 
                case['duration'] = duration 
                case['action'] = action
                case['message'] = str(msg.id)
                document = {"$set": {str(server.id):{
                    "channel": self.data[str(server.id)]['channel'],
                    "status": self.data[str(server.id)]['status'],
                    "case#": self.data[str(server.id)]["case#"] + 1,
                    "cases": self.data[str(server.id)]['cases'] + [case]
                }}}
                self.col.update_one({"auth": True}, document)
            else:
                embed = discord.Embed(color=color, timestamp=datetime.utcnow())
                embed.set_author(name="{} | Case {:,}".format(action, self.data[str(server.id)]['case#']+1))
                embed.add_field(name=f"User", value=f"{user} ({user.mention})")
                embed.add_field(name=f"Moderator", value=f"{mod} ({mod.mention})")
                embed.add_field(name=f"Reason", value=reason, inline=False)
                embed.set_footer(text=f"ID: {user.id}")
                msg = await mod_chan.send(embed=embed)
                case = {}
                case['id'] = case1 + 1
                case['user'] = str(user.id)
                case['mod'] = str(self.bot.user.id)
                case['time'] = time.strftime('%d-%m-%Y')
                case['reason'] = reason 
                case['action'] = action
                case['message'] = str(msg.id)
                document = {"$set": {str(server.id):{
                    "channel": self.data[str(server.id)]['channel'],
                    "status": self.data[str(server.id)]['status'],
                    "case#": self.data[str(server.id)]['case#'] + 1,
                    "cases": self.data[str(server.id)]['cases'] + [case]
                }}}
                self.col.update_one({"auth": True}, document)

    async def warn_user(self, ctx, user, reason):
        self.warns = self.warndb.find_one()
        self.data = self.col.find_one()
        self.mutes = self.muted.find_one()
        self.set = self.settings.find_one()
        server = ctx.guild
        if not str(server.id) in self.warns:
            await self.send_log(ctx.guild,'Warn',user, reason)
        else:
            await self.send_log(ctx.guild,'Warn',user,reason)
            cases = self.data[str(server.id)]["cases"]
            found_cases = [c for c in cases if c["user"] == str(user.id)]
            found_warns = [c for c in found_cases if c["action"] == "Warn"]
            found_warns=len(found_warns)+1
			
            found=False
            myquery = {"server-id": str(ctx.guild.id)}
            mydoc = self.config.find(myquery)
            for x in mydoc:
              found=True
            if not found:
              return
            rlist=x["rules"]
            if rlist==[]:
              return
            threshold=None
            for rule in rlist:
              if int(rule[0])==found_warns:
                threshold=rule
                punishment=rule[1]	
			
            if not threshold:
              return 
            if punishment == "kick":
                try:
                    await user.kick(reason="Auto-Kick, Hit the warning limit.")
                except discord.Forbidden:
                    pass
                
                await self.send_log(ctx.guild, "Kick", user, "Hit the warning limit.")
            if punishment == "ban":
                try:
                    await user.ban(reason="Auto-Ban, Hit the warning limit.")
                except discord.Forbidden:
                    pass 
                await self.send_log(ctx.guild, "Ban", user, "Hit the warning limit.")
            if punishment == "pmute":
                muted_role = self.set[str(server.id)]["muted-role"]
                mute = server.get_role(muted_role)
                if not mute:
                    return 
                try:
                    await user.add_roles(mute, reason="Auto-Mute, Hit the warning limit.")
                except discord.Forbidden:
                    pass 
                await self.send_log(ctx.guild, "Pmute", user, "Hit the warning limit.")
            if punishment == "tempmute":
                muted_role = self.set[str(server.id)]["muted-role"]
                mute = server.get_role(muted_role)
                if not mute:
                    return 
                try:
                    await user.add_roles(mute, reason="Auto-Mute, Hit the warning limit.")
                except discord.Forbidden:
                    pass 
                if not str(server.id) in self.mutes:
                    doc = {"$set": {str(server.id):{
                        "muted": {
                            str(user.id): {
                                "muted-time": threshold[3],
                                "mod": str(ctx.author.id),
                                "reason": "Hitting the warning limit."
                            }
                        }
                    }}}
                    self.muted.update_one({"auth": True}, doc)
                else:
                    muted_list = self.mutes[str(server.id)]["muted"]
                    doc = {"$set": {str(server.id):{
                       "muted": {**muted_list, str(user.id):{
                           "muted-time": threshold[3],
                           "mod": str(ctx.author.id),
                           "reason": "Hitting the warning limit."
                        }}
                    }}}
                    self.muted.update_one({"auth": True}, doc)
                await self.send_log(ctx.guild,'Mute', user, "Automute for reaching the warning threshold.",threshold[3])
                await asyncio.sleep(int(threshold[2])*60)
                doc = {"$set": {str(server.id):{
                    "muted": {k:v for k,v in muted_list.items() if k != str(user.id)}
                }}}
                self.muted.update_one({"auth": True}, doc)
                if mute in user.roles:
                    await user.remove_roles(mute, reason="Auto-Unmute, time up.")
                else:
                    return
    

    async def spamming(self, server, user, channel,ctx):
        await channel.send(f'{user.mention} Stop spamming!', delete_after=3)
        self.data = self.spam.find_one()
        self.set = self.settings.find_one()
        document = {"$set": {str(server.id):{
            "spams": self.data[str(server.id)]["spams"] + 1,
            "anti-spam": self.data[str(server.id)]["anti-spam"],
            "duration": self.data[str(server.id)]["duration"],
            "messages": self.data[str(server.id)]["messages"],
            "punishments": self.data[str(server.id)]["punishments"],
            "stopped": self.data[str(server.id)]["stopped"] + 1
        }}}
        self.spam.update_one({"auth": True}, document)
        punishments = self.data[str(server.id)]["punishments"]
        messages = self.data[str(server.id)]["messages"]
        seconds = self.data[str(server.id)]["duration"]
        for punishment in punishments:
            if punishment == "kick":
                try:
                    await user.send(f"Hello. You have been kicked from **{server.name}**! Reaching the ({self.data[str(server.id)]['messages']}/{self.data[str(server.id)]['duration']}) limit for spamming.")
                except discord.Forbidden:
                    pass 
                try:
                    await user.kick(reason="Spamming")
                except discord.Forbidden:
                    return
                await self.send_log(server, "Kick", user, f"Reaching the ({self.data[str(server.id)]['messages']}/{self.data[str(server.id)]['duration']}) limit for spamming.")
            elif punishment == "ban": 
                try:
                    await user.send(f"Hello. You have been banned from **{server.name}**! Reaching the ({self.data[str(server.id)]['messages']}/{self.data[str(server.id)]['duration']}) limit for spamming.")
                except discord.Forbidden:
                    pass 
                try:
                    await user.ban(reason="Spamming")
                except discord.Forbidden:
                    return
                await self.send_log(server, "Ban", user, f"Reaching the ({self.data[str(server.id)]['messages']}/{self.data[str(server.id)]['duration']}) limit for spamming.")
            elif punishment == "warn":
                try:
                    await user.send(f"Hello. You have been warned in **{server.name}**! Reaching the ({self.data[str(server.id)]['messages']}/{self.data[str(server.id)]['duration']}) limit for spamming.")
                except discord.Forbidden:
                    return
                await self.warn_user(ctx, user, f"Reaching the ({self.data[str(server.id)]['messages']}/{self.data[str(server.id)]['duration']}) limit for spamming.")
            elif punishment == "pmute":
                muted_role = self.set[str(server.id)]["muted-role"]
                mute = server.get_role(muted_role)
                if not mute:
                    return 
                try:
                    await user.add_roles(mute, reason="Auto-Mute, spamming.")
                except discord.Forbidden:
                    return
                await self.send_log(server, "Pmute", user, f"Reaching the ({messages} messages/{seconds}) limit for spamming.")
            elif punishment == "tempmute":
                muted_role = self.set[str(server.id)]["muted-role"]
                mute = server.get_role(muted_role)
                if not mute:
                    return 
                try:
                    await user.add_roles(mute, reason="Spamming")
                except discord.Forbidden:
                    return
                await self.send_log(server, "Mute", user, f"Reaching the ({messages} messages/{seconds}) limit for spamming.", duration=punishments["tempmute"]["time"])
                await asyncio.sleep(punishments['tempmute']['duration'])
                if mute in user.roles:
                    await user.remove_roles(mute, reason="Auto-Unmute, time up.")
                    await self.send_log(server, "Unmute", user, f"Automatic unmute from the mute made {punishments['tempmute']['time']} ago by {self.bot.user}.")
                else:
                    return
            

    @commands.group(aliases=['anti-spam'])
    @commands.has_permissions(manage_guild=True)
    async def antispam(self, ctx):
        if not ctx.invoked_subcommand:
            embed = discord.Embed(color=self.bot.embed)
            embed.set_author(name=ctx.guild, icon_url=ctx.guild.icon_url)
            embed.description = f"""
            These are the current punishments: `warn`,`kick`,`ban`,`tempmute`,`pmute`
            You can set more than 1 punishment.
            """
            embed.add_field(name=f"?anti-spam toggle", value=f"""
            Turns on and off like a switch. If enabled it disables it, so forth.
            """)
            embed.add_field(name=f"?anti-spam set <time> <messages>", value=f"""
            This sets the anitspam time. If you sent 5 messages in 3 seconds it will trigger the anti-spam.
            Ex. `?anti-spam set 5s 3`
            This will return 3 messages in 5 seconds.
            """)
            embed.add_field(name=f"?anti-spam punishment add <punishment> [time]", value=f"""
            Adds a punishment for the user if he/she hits the anti-spam limit.
            You shall specify a time if you wish to tempmute the user.
            """)
            embed.add_field(name=f"?anti-spam punishment remove <punishment>", value=f"""
            Removes the punishment from the anti-spam punishments. If he/she starts to spam it won't give this punishment to him/her.
            """)
            embed.add_field(name=f"?anti-spam settings", value=f"""
            Shows all of the current configurations for anti-spam.
            """)
            await ctx.send(embed=embed)

    @antispam.command(description="See all of the current configurations for anti-spam.", aliases=['configs', 'configurations'], usage=['antispam settings'])
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx):
        self.data = self.spam.find_one()
        server = ctx.guild 
        if not str(server.id) in self.data:
            document = {"$set": {str(server.id):{
                "spams": 0,
                "anti-spam": "disabled",
                "duration": 0,
                "messages": 0,
                "punishments": {},
                "stopped": 0
            }}}
            self.spam.update_one({"auth": True}, document)
            await ctx.send(f"{self.bot.x} Your server doesn't have any anti-spam configurations.")
        spam = self.data[str(server.id)]["anti-spam"]
        if spam == "enabled":
            spam = f'{self.bot.check} Anti-spam is enabled.'
        else:
            spam = f'{self.bot.x} Anti-spam is disabled.'
        messages = self.data[str(server.id)]["messages"]
        duration = self.data[str(server.id)]["duration"]
        lmt = duration
        time1 = lmt
        days = time1 // (24 * 3600)
        time1 - time1 % (24 * 3600)
        hours = time1 // 3600 
        time1 %= 3600
        minutes = time1 // 60
        time1 %= 60
        seconds = time1 
        time_str = " ".join((f'{y} {x}' for x,y in vars().items() if x in ('days','hours','minutes','seconds') if y > 0))
        punishments = self.data[str(server.id)]["punishments"]
        puni = [f"{x} - `{y['time']}`" if y else f"{x}" for x,y in punishments.items()]
        formatted = [f"**{x}**. {y}" for x,y in enumerate(puni, start=1)]
        embed = discord.Embed(color=self.bot.embed)
        embed.set_author(name=server.name, icon_url=server.icon_url)
        embed.add_field(name="Anti Spam", value=spam, inline=False)
        embed.add_field(name="Spams Stopped by Argon", value=self.data[str(server.id)]["stopped"])
        embed.add_field(name="Anti Spam Workings", value=f"**{messages}** messages in **{time_str}**", inline=False)
        embed.add_field(name="Anti Spam Punishments", value="\n".join(formatted))
        await ctx.send(embed=embed)

    @antispam.command(description="Enable or disable anti-spam depending on what it is currently on.", aliases=['t'], usage=['antispam toggle'])
    @commands.has_permissions(manage_guild=True)
    async def toggle(self, ctx):
        server = ctx.guild 
        self.data = self.spam.find_one()
        if not str(server.id) in self.data:
            document = {"$set": {str(server.id):{
                "spams": 0,
                "anti-spam": "disabled",
                "duration": 0,
                "messages": 0,
                "punishments": {},
                "stopped": 0
            }}}
            self.spam.update_one({"auth": True}, document)
            return await ctx.send(f"{self.bot.check} Successfully disabled anti-spam.")
        if self.data[str(server.id)]["anti-spam"] == "disabled":
            document = {"$set": {str(server.id):{
                "spams": self.data[str(server.id)]["spams"],
                "anti-spam": "enabled",
                "duration": self.data[str(server.id)]["duration"],
                "messages": self.data[str(server.id)]["messages"],
                "punishments": self.data[str(server.id)]["punishments"],
                "stopped": self.data[str(server.id)]["stopped"]
            }}}
            self.spam.update_one({"auth": True}, document)
            await ctx.send(f"{self.bot.check} Successfully enabled anti-spam.")
        elif self.data[str(server.id)]["anti-spam"] == "enabled":
            document = {"$set": {str(server.id):{
                "spams": self.data[str(server.id)]["spams"],
                "anti-spam": "disabled",
                "duration": self.data[str(server.id)]["duration"],
                "messages": self.data[str(server.id)]["messages"],
                "punishments": self.data[str(server.id)]["punishments"],
                "stopped": self.data[str(server.id)]["stopped"]
            }}}
            self.spam.update_one({"auth": True}, document)
            await ctx.send(f"{self.bot.check} Successfully disabled anti-spam.")

    @antispam.command()
    async def set(self, ctx, lmt: typing.Optional[convtime] = None, messages: int = None):
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
        time_str = " ".join((f'{y} {x}' for x,y in vars().items() if x in ('days','hours','minutes','seconds') if y > 0))
        self.data = self.spam.find_one()
        server = ctx.guild 
        if not lmt:
            return await ctx.send(f"{self.bot.x} You need specify a time for me to set as the amount of seconds.")
        if not messages:
            return await ctx.send(f"{self.bot.x} You need to specify the amount of messages you want me to stop the spammer at.")
        if not str(server.id) in self.data:
            document = {"$set":{str(server.id):{
                "spams": 0,
                "anti-spam": "disabled",
                "duration": lmt,
                "messages": messages,
                "punishments": {},
                "stopped": 0
            }}}
            self.spam.update_one({"auth": True}, document)
            await ctx.send(f"{self.bot.check} I will now stop spammers. If there are **{messages}** messages sent in **{time_str}**, I will delete those messages automatically.")
        else:
            document = {"$set":{str(server.id):{
                "spams": self.data[str(server.id)]["spams"],
                "anti-spam": self.data[str(server.id)]["anti-spam"],
                "duration": lmt,
                "messages": messages,
                "punishments": self.data[str(server.id)]["punishments"],
                "stopped": self.data[str(server.id)]["stopped"]
            }}}
            self.spam.update_one({"auth": True}, document)
            await ctx.send(f"{self.bot.check} I will now stop spammers. If there are **{messages}** messages sent in **{time_str}**, I will delete those messages automatically.")

    @antispam.command(description="Add a punishment to the user if they spam.", )
    async def punishment(self, ctx, action: str = None, punishment = None, lmt: typing.Optional[convtime] = None):
        self.data = self.spam.find_one()
        server = ctx.guild 
        if not punishment:
            return await ctx.send(f"{self.bot.x} You need to specify a punishment for me to add.")
        punishments = [
            "kick",
            "pmute",
            "ban",
            "tempmute",
            "warn"
        ]
        if not punishment.lower() in punishments:
            return await ctx.send(f"{self.bot.x} The punishment you specified is not a punishment that you can use.\nCurrent Punishments:\nKick, Ban, Warn, Tempmute, Pmute, Warn")
        if action.lower() == "add": 
            if not str(server.id) in self.data:
                if punishment.lower() == "tempmute":
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
                    time_str = " ".join((f'{y} {x}' for x,y in vars().items() if x in ('days','hours','minutes','seconds') if y > 0))
                    document1 = {"$set": {str(server.id):{
                        "spams": 0,
                        "anti-spam": "disabled",
                        "duration": 0,
                        "messages": 0,
                        "punishments": {punishment:{"duration": lmt, "time": time_str}},
                        "stopped": 0
                    }}}
                    self.spam.update_one({"auth": True}, document1)
                    await ctx.send(f"{self.bot.check} Successfully added **{punishment}** to the warning-punishments. The user will be muted for **{time_str}**.")
                else:
                    document1 = {"$set": {str(server.id):{
                        "spams": 0,
                        "anti-spam": "disabled",
                        "duration": 0,
                        "messages": 0,
                        "punishments": {punishment:None},
                        "stopped": 0
                    }}}
                    self.spam.update_one({"auth": True}, document1)
                    await ctx.send(f"{self.bot.check} Successfully added **{punishment}** to the warning-punishments.")
            else:
                punishments = self.data[str(server.id)]["punishments"]
                if punishment.lower() in punishments:
                    return await ctx.send(f"{self.bot.x} That punishment is already in the warning-punishments.")
                if punishment.lower() == "tempmute":
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
                    time_str = " ".join((f'{y} {x}' for x,y in vars().items() if x in ('days','hours','minutes','seconds') if y > 0))
                    document1 = {"$set": {str(server.id):{
                        "spams": self.data[str(server.id)]["spams"],
                        "anti-spam": self.data[str(server.id)]["anti-spam"],
                        "duration": self.data[str(server.id)]["duration"],
                        "messages": self.data[str(server.id)]["messages"],
                        "punishments": {**punishments, punishment:{"duration": lmt, "time": time_str}},
                        "stopped": self.data[str(server.id)]["stopped"]
                    }}}
                    self.spam.update_one({"auth": True}, document1)
                    await ctx.send(f"{self.bot.check} Successfully added **{punishment}** to the spamming punishments. The user will be muted for **{time_str}**.")
                else:
                    document1 = {"$set": {str(server.id):{
                        "spams": self.data[str(server.id)]["spams"],
                        "anti-spam": self.data[str(server.id)]["anti-spam"],
                        "duration": self.data[str(server.id)]["duration"],
                        "messages": self.data[str(server.id)]["messages"],
                        "punishments": {**punishments, punishment:None},
                        "stopped": self.data[str(server.id)]["stopped"]
                    }}}
                    self.spam.update_one({"auth": True}, document1)
                    await ctx.send(f"{self.bot.check} Successfully added **{punishment}** to the spamming punishments.")
        elif action.lower() == "remove":
            if not str(server.id) in self.data:
                document1 = {"$set": {str(server.id):{
                        "spams": 0,
                        "anti-spam": "disabled",
                        "duration": 0,
                        "messages": 0,
                        "punishments": {},
                        "stopped": []
                }}}
                self.spam.update_one({"auth": True}, document1)
                await ctx.send(f"{self.bot.x} Your server doesn't have any punishments.")
            else:
                punishments = self.data[str(server.id)]["punishments"]
                if not punishment.lower() in punishments:
                    return await ctx.send(f"{self.bot.x} That punishment is not in the spamming punishments.")
                document1 = {"$set": {str(server.id):{
                    "spams": self.data[str(server.id)]["spams"],
                    "anti-spam": self.data[str(server.id)]["anti-spam"],
                    "duration": self.data[str(server.id)]["duration"],
                    "messages": self.data[str(server.id)]["messages"],
                    "punishments": {k:v for k,v in punishments.items() if k != punishment.lower()},
                    "stopped": self.data[str(server.id)]["stopped"]
                }}}
                self.spam.update_one({"auth": True}, document1)
                await ctx.send(f"{self.bot.check} Successfully removed **{punishment}** from the spamming punishments.")
        else:
            return await ctx.send(f"{self.bot.x} that is not an action for this command. Use `set` or `remove`.")

    @antispam.command(description="See all of the current punishments for your server's anti-spam.", aliase=[], usage=['antispam punishments'])
    @commands.has_permissions(manage_guild=True)
    async def punishments(self, ctx):
        self.data = self.spam.find_one()
        server = ctx.guild 
        if not str(server.id) in self.data:
            return await ctx.send(f"{self.bot.x} This server doesn't have any punishments for spamming.")
        punishments = self.data[str(server.id)]["punishments"]
        puni = [f"{x} - `{y['time']}`" if y else f"{x}" for x,y in punishments.items()]
        formatted = [f"**{x}**. {y}" for x,y in enumerate(puni, start=1)]
        embed = discord.Embed(color=self.bot.embed)
        embed.set_author(name=server, icon_url=server.icon_url)
        embed.description = "\n".join(formatted)
        await ctx.send(embed=embed)

            
    @commands.Cog.listener()
    async def on_message(self, message):  
        guild=message.guild
        server = message.guild
        data = self.spam.find_one()
        try:
            if str(guild.id) not in self.data:
                return
        except:
            return
        spam = data[str(guild.id)]['anti-spam']
        if spam == "disabled":
            return
        messages_count = data[str(guild.id)]["messages"]
        seconds = data[str(guild.id)]["duration"]
        if messages_count == 0:
            return 
        if seconds == 0:
            return
        channel=message.channel
        if isinstance(channel, discord.TextChannel):
                        time = datetime.utcnow() - timedelta(seconds=seconds)
                        messages = await channel.history(after=time).flatten()
                        mess_auth = defaultdict(list)
                        for mess in messages:
                            mess_auth[mess.author].append(mess)
                        for k, v in mess_auth.items():
                            if len(v) >= messages_count:
                                user = mess_auth[k][0].author
                                await channel.delete_messages(v)
                                await self.spamming(server,user, channel,message)
        #await asyncio.sleep(seconds)
def setup(bot):
    bot.add_cog(Anti_Spam(bot))
