import discord 
from discord.ext import commands 
from pymongo import MongoClient as mcl 
from datetime import datetime 
import time
from utils import arg
import re
import asyncio
import typing
from collections import Counter, defaultdict


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



class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.client = mcl("mongodb://o:o99999@ds337377.mlab.com:37377/modtest")
        self.db = self.client['modtest']
        self.col = self.db['modlog']
        self.settings = self.db['settings']
        self.muted = self.db["muted"]
        self.warndb = self.db['warning']
        self.config=self.db['automod']


    async def warn_user(self, ctx, user, reason):
        self.warns = self.warndb.find_one()
        self.data = self.col.find_one()
        self.mutes = self.muted.find_one()
        self.set = self.settings.find_one()
        server = ctx.guild 
        if not str(server.id) in self.warns:
            document1 = {"$set": {str(server.id):{
                "warn-threshold": 0,
                "warn-punishments": {}
            }}}
            self.warndb.update_one({"auth": True}, document1)
            await self.send_log(ctx, user, reason, "Warn")
            await ctx.send(f"Warned **{user}** successfully, this is their 1st warning.")
        else:
            await self.send_log(ctx, user, reason, "Warn")
            cases = self.data[str(server.id)]["cases"]
            found_cases = [c for c in cases if c["user"] == str(user.id)]
            found_warns = [c for c in found_cases if c["action"] == "Warn"]
            await ctx.send(f":incoming_envelope: Warned **{user}** successfully, this is their {self.prefixfy(len(found_warns) + 1)} warning.")
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
                await self.send_log(ctx, user, "Hit the warning limit.", "Kick")
            if punishment == "ban":
                try:
                    await user.ban(reason="Auto-Ban, Hit the warning limit.")
                except discord.Forbidden:
                    pass 
                await self.send_log(ctx, user, "Hit the warning limit.", "Ban")
            if punishment == "pmute":
                muted_role = self.set[str(server.id)]["muted-role"]
                mute = server.get_role(muted_role)
                if not mute:
                    return 
                try:
                    await user.add_roles(mute, reason="Auto-Mute, Hit the warning limit.")
                except discord.Forbidden:
                    pass 
                await self.send_log(ctx, user, "Hit the warning limit.", "Pmute")
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
                await self.send_log(ctx, user, "Automute for reaching the warning threshold.",'Mute',threshold[3])
                await asyncio.sleep(int(threshold[2])*60)
                doc = {"$set": {str(server.id):{
                    "muted": {k:v for k,v in muted_list.items() if k != str(user.id)}
                }}}
                self.muted.update_one({"auth": True}, doc)
                if mute in user.roles:
                    await user.remove_roles(mute, reason="Auto-Unmute, time up.")
                else:
                    return

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

    async def embed_mk(self, ctx, cases, user2):
        server = ctx.guild
        embed = discord.Embed(color=self.bot.embed, timestamp = datetime.utcnow())
        found_cases = [c for c in cases if c["user"] == str(user2.id)]
        for case in cases:
            mod = await self.bot.fetch_user(int(case['mod']))
            embed.set_author(name=f"{user2}", icon_url=user2.avatar_url)
            if case["action"] == "Mute":
                embed.add_field(name=f"#{case['id']} | {case['action']}", value=f"""
                **Moderator:** {mod}
                **Reason:** {case['reason']}
                **Duration:** {case['duration']}
                """, inline=False)
            else:
                embed.add_field(name=f"#{case['id']} | {case['action']}", value=f"""
                **Moderator:** {mod}
                **Reason:** {case['reason']}
                """, inline=False)
            embed.set_footer(text=f"{len(found_cases)} actions found.")
        return embed

    async def send_log(self, ctx, user, reason, action, duration = None):
        self.data= self.col.find_one()
        server = ctx.guild 
        print(server.id)
        if not reason:
            reason = "No reason provided."
        if not str(server.id) in self.data:
            print('Server Found In Data\n\n')
            if action == "Mute" or action=="Tempban":
                case = {}
                case['id'] = 1 
                case['user'] = str(user.id)
                case['mod'] = str(ctx.author.id)
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
            case['mod'] = str(ctx.author.id)
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
        mod_chan = server.get_channel(int(self.data[str(server.id)]["channel"]))
        if not mod_chan:
            if action == "Mute" or action == "Tempban":
                case = {}
                case['id'] = self.data[str(server.id)]['case#'] + 1 
                case['user'] = str(user.id)
                case['mod'] = str(ctx.author.id)
                case['action'] = action
                case['time'] = time.strftime('%d-%m-%Y')
                case['reason'] = reason 
                case['duration'] = duration
                document = {"$set": {str(server.id):{
                    "channel": self.data[str(server.id)]["channel"],
                    "status": self.data[str(server.id)]["status"],
                    "case#": self.data[str(server.id)]["case#"] + 1,
                    "cases": self.data[str(server.id)]['cases'] + [case]
                }}}
                self.col.update_one({"auth": True}, document)
            else:
                case = {}
                case['id'] = self.data[str(server.id)]['case#'] + 1
                case['user'] = str(user.id)
                case['mod'] = str(ctx.author.id)
                case['action'] = action
                case['time'] = time.strftime('%d-%m-%Y')
                case['reason'] = reason 
                document = {"$set": {str(server.id):{
                    "channel": self.data[str(server.id)]["channel"],
                    "status": self.data[str(server.id)]["status"],
                    "case#": self.data[str(server.id)]["case#"] + 1,
                    "cases": self.data[str(server.id)]['cases'] + [case]
                }}}
                self.col.update_one({"auth": True}, document)
            return
        if self.data[str(server.id)]["status"] == "disabled":
            if action == "Mute" or action == "Tempban":
                case = {}
                case['id'] = self.data[str(server.id)]['case#'] + 1
                case['user'] = str(user.id)
                case['mod'] = str(ctx.author.id)
                case['action'] = action
                case['time'] = time.strftime('%d-%m-%Y')
                case['reason'] = reason 
                case['duration'] = duration
                document = {"$set": {str(server.id):{
                    "channel": self.data[str(server.id)]["channel"],
                    "status": self.data[str(server.id)]["status"],
                    "case#": self.data[str(server.id)]["case#"] + 1,
                    "cases": self.data[str(server.id)]['cases'] + [case]
                }}}
                self.col.update_one({"auth": True}, document)
            else:
                case = {}
                case['id'] = self.data[str(server.id)]['case#'] + 1
                case['user'] = str(user.id)
                case['mod'] = str(ctx.author.id)
                case['action'] = action
                case['time'] = time.strftime('%d-%m-%Y')
                case['reason'] = reason 
                document = {"$set": {str(server.id):{
                    "channel": self.data[str(server.id)]["channel"],
                    "status": self.data[str(server.id)]["status"],
                    "case#": self.data[str(server.id)]["case#"] + 1,
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
            mod = ctx.author 
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
                case['id'] = self.data[str(server.id)]["case#"] + 1
                case['user'] = str(user.id)
                case['mod'] = str(ctx.author.id)
                case['time'] = time.strftime('%d-%m-%Y')
                case['reason'] = reason 
                case['duration'] = duration 
                case['action'] = action
                case['message'] = str(msg.id)
                document = {"$set": {str(server.id):{
                    "channel": self.data[str(server.id)]["channel"],
                    "status": self.data[str(server.id)]["status"],
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
                case['id'] = self.data[str(server.id)]["case#"] + 1
                case['user'] = str(user.id)
                case['mod'] = str(ctx.author.id)
                case['time'] = time.strftime('%d-%m-%Y')
                case['reason'] = reason 
                case['action'] = action
                case['message'] = str(msg.id)
                document = {"$set": {str(server.id):{
                    "channel": self.data[str(server.id)]["channel"],
                    "status": self.data[str(server.id)]["status"],
                    "case#": self.data[str(server.id)]["case#"] + 1,
                    "cases": self.data[str(server.id)]['cases'] + [case]
                }}}
                self.col.update_one({"auth": True}, document)

    @commands.group()
    @commands.has_permissions(manage_guild=True)
    async def modlog(self, ctx):
        if not ctx.invoked_subcommand:
            embed = discord.Embed(color=self.bot.embed)
            embed.set_author(name=ctx.guild, icon_url=ctx.guild.icon_url)
            embed.add_field(name=f"?modlog channel #channel",  value=f"""
            This feature will log everything that moderators do. 
            E.g ?kick @BrendanTheBigBoi#6908 Spamming.
            This will log it in the channel that you wish to set.
            """)
            embed.add_field(name=f"?modlog toggle", value=f"""
            This will set the modlog to enable or disable, depending on what it is on.
            If the modlog is disabled it won't log anything that the moderators do, but it will add it to the cases!
            """)
            embed.add_field(name=f"?modlog from [@User]", value=f"""
            This shows all of the actions given to that certain user.
            It will also show the moderator, user, and if it was a mute, the duration!
            Note: If you don't mention a user it will automatically show your moderation loggings.
            """)
            embed.add_field(name=f"?modlog settings", value=f"""
            See all of the current server configurations. 
            Modlog channel, current status(enabled or disabled), muted role, and current amount of cases the server has.
            """)
            embed.add_field(name=f"?modlog case <case_num>", value=f"""
            See all of the information on a case.
            It will automatically put the duration in the embed description if it is a mute or tempmute.
            """)
            embed.add_field(name=f"?modlog edit <case_num> <reason>", value=f"""
            Edit the case reason. If you aren't the moderator that gave this case to the user you won't be allowed to use it.
            """)
            await ctx.send(embed=embed)

    @modlog.command(descrption="Set the moderation log channel. Log every action the moderator makes.", aliases=['chan', 'c'], usage=['modlog channel', 'modlog channel #channel'])
    @commands.has_permissions(manage_guild=True)
    async def channel(self, ctx, channel: discord.TextChannel = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not channel:
            channel = ctx.channel 
        if not str(server.id) in self.data:
            data = {"$set": {str(server.id):{
                "channel": str(channel.id),
                "status": "disabled",
                "case#": 0,
                "cases": []
            }}}
            self.col.update_one({"auth": True}, data)
            await ctx.send(F"{self.bot.check} Successfully set the modlog to: {channel.mention}")
        data = {"$set": {str(server.id):{
            "channel": str(channel.id),
            "status": self.data[str(server.id)]['status'],
            "case#": self.data[str(server.id)]['case#'],
            "cases": self.data[str(server.id)]['cases']
        }}}
        self.col.update_one({"auth": True}, data)
        await ctx.send(F"{self.bot.check} Successfully set the modlog to: {channel.mention}")

    @channel.error 
    async def channel_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(F"{self.bot.x} I couldn't find that channel.")

    @modlog.command(description="Enable or disable the modlog, depending on what it is currently on.", aliases=['t', 'tog'], usage=['modlog toggle'])
    @commands.has_permissions(manage_guild=True)
    async def toggle(self, ctx):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not str(server.id) in self.data:
            data = {"$set": {str(server.id):{
                "channel": "not set",
                "status": "enabled",
                "case#": 0,
                "cases": []
            }}}
            self.col.update_one({"auth": True}, data)
            await ctx.send(f"{self.bot.check} Successfully enabled the modlog.")
        status = self.data[str(server.id)]['status']
        if status == "enabled":
            data = {"$set": {str(server.id):{
                "channel": self.data[str(server.id)]['channel'],
                "status": "disabled",
                "case#": self.data[str(server.id)]['case#'],
                "cases": self.data[str(server.id)]['cases']
            }}}
            self.col.update_one({"auth": True}, data)
            await ctx.send(f"{self.bot.check} Successfully disabled the modlog.")
        if status == "disabled":
            data = {"$set": {str(server.id):{
                "channel": self.data[str(server.id)]['channel'],
                "status": "enabled",
                "case#": self.data[str(server.id)]['case#'],
                "cases": self.data[str(server.id)]['cases']
            }}}
            self.col.update_one({"auth": True}, data)
            await ctx.send(f"{self.bot.check} Successfully enabled the modlog.")

    @modlog.command(description="See all of the given punishments to a certain user.", aliases=['f', 'from', 'for'], usgae=['modlog from @user', 'modlog from'])
    @commands.has_permissions(manage_channels=True)
    async def fo(self, ctx, user2: discord.Member = None):
        self.data = self.col.find_one()
        server = ctx.guild
        if not user2:
            user2 = ctx.author 
        if not str(server.id) in self.data:
            return await ctx.send(f"{self.bot.x} I can't find any loggings in the server. Please make sure that you have the modlog setup!")
        cases = self.data[str(server.id)]['cases']
        found_cases = [c for c in cases if c["user"] == str(user2.id)]
        if len(found_cases) == 0:
            return await ctx.send(f"{self.bot.x} I believe this user doesn't have any moderation loggings.")
        embed = await self.embed_mk(ctx, found_cases[:8], user2)
        message = await ctx.send(embed=embed)
        if len(found_cases) > 8:
            await message.add_reaction("◀")
            await message.add_reaction("❌")
            # await message.add_reaction("🇮")
            await message.add_reaction("▶")
        def reactioncheck(reaction, user):
            if user == ctx.author:
                if reaction.message.id == message.id:
                    if reaction.emoji == "▶" or reaction.emoji == "❌" or reaction.emoji == "◀" or reaction.emoji == "🇮":
                        return True
        x = 0
        while True:
            reaction, user3 = await self.bot.wait_for("reaction_add", check=reactioncheck)
            if reaction.emoji == "◀":
                x -= 8
                if x < 0:
                    x = 0
                await message.remove_reaction("◀", user3)
            elif reaction.emoji == "❌":
                await message.delete()
            elif reaction.emoji == "▶":
                x += 8
                if x > len(found_cases):
                    x = len(found_cases) - 8
            embed = await self.embed_mk(ctx, found_cases[x:x+8], user2)
            await message.edit(embed=embed)
            await message.remove_reaction("▶", user3)

    @modlog.command(description=f"See all of the information for a case.", aliases=['vc', 'viewcase'], usage=['modlog case <number>', 'modlog case 3'])
    @commands.has_permissions(manage_guild=True)
    async def case(self, ctx, case_number: int = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not case_number:
            return await ctx.send(f"{self.bot.x} You need to specify the case number you would like to see.")
        if not str(server.id) in self.data:
            return await ctx.send(f"{self.bot.x} I am unable to find a case with that id.")
        cases = self.data[str(server.id)]['cases']
        found_case = [c for c in cases if c['id'] == case_number]
        if len(found_case) == 0:
            return await ctx.send(f"{self.bot.x} I am unable to find a case with that id.")
        case = found_case[0]
        action = case['action']
        color = self.bot.embed
        if action == "Warn":
            color = 0xfffa77
        if action == "Mute":
            color = 0xff68e5
        if action == "Ban":
            color = 0xf08080
        if action == "Kick":
            color = 0xf48942
        if action == "Unmute":
            color = 0x42f4a7
        if action == "Unban": 
            color = 0x42f4a7
        if action == "Softban": 
            color = 0xfdd0ff
        if action == "Tempban":
            color = 0xff68e5
        if action == "Pmute":
            color = 0xf48942
        embed = discord.Embed(color=color)
        user = await self.bot.fetch_user(case['user'])
        mod = await self.bot.fetch_user(case['mod'])
        embed.set_author(name=f"{action} | Case {case['id']}")
        if action == "Mute" or action == "Tempmute":
            embed.description = f"""
            **Offender:** {user} {user.mention}
            **Duration:** {case['duration']}
            **Reason:** {case['reason']}
            **Respected Moderator:** {mod}
            """
        else:
            embed.description = f"""
            **Offender:** {user} {user.mention}
            **Reason:** {case['reason']}
            **Respected Moderator:** {mod}
            """
        await ctx.send(embed=embed)

    @modlog.command(description="Provide a reason for the modlog case.", aliases=[], usage=['modlog edit <case> <reason>', 'modlog edit 1 Breaking the rules.'])
    async def edit(self, ctx, case_number: int = None, *, reason = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not case_number:
            return await ctx.send(f"{self.bot.x} You need to provide the case number you would like to edit.")
        if not str(server.id) in self.data:
            return await ctx.send(f"{self.bot.x} I am unable to find a case with that id.")
        cases = self.data[str(server.id)]['cases']
        found_case = [c for c in cases if c['id'] == case_number]
        if len(found_case) == 0:
            return await ctx.send(f"{self.bot.x} I am unable to find a case with that id.")
        case = found_case[0]
        action = case['action']
        color = self.bot.embed
        if action == "Warn":
            color = 0xfffa77
        if action == "Mute":
            color = 0xff68e5
        if action == "Ban":
            color = 0xf08080
        if action == "Kick":
            color = 0xf48942
        if action == "Unmute":
            color = 0x42f4a7
        if action == "Unban": 
            color = 0x42f4a7
        if action == "Softban": 
            color = 0xfdd0ff
        if action == "Tempban":
            color = 0xff68e5
        if action == "Pmute":
            color = 0xf48942
        if not str(ctx.author.id) in case['mod']:
            return await ctx.send(F"{self.bot.x} You don't have ownership to this case. In other words, you didn't give this action to the user.")
        embed = discord.Embed(color=color)        
        user = await self.bot.fetch_user(case['user'])
        mod = await self.bot.fetch_user(case['mod'])
        embed.set_author(name=f"{action} | Case {case['id']}")
        try:
            chan = server.get_channel(int(self.data[str(server.id)]['channel']))
            msg = await chan.fetch_message(case['message'])
            embeds = msg.embeds[0] 
            if action == "Mute" or action == "Tempmute":
                embed.description = f"""
                **Offender:** {user} {user.mention}
                **Duration:** {case['duration']}
                **Reason:** {reason}
                **Respected Moderator:** {mod}
                """
                await msg.edit(embed=embed)
                case['reason'] = reason
            else:
                embed.description = f"""
                **Offender:** {user} {user.mention}
                **Reason:** {reason}
                **Respected Moderator:** {mod}
                """
                await msg.edit(embed=embed)
                case['reason'] = reason
        except discord.errors.NotFound:
            pass
        document = {"$set": {str(server.id):{
            "channel": self.data[str(server.id)]["channel"],
            "status": self.data[str(server.id)]["status"],
            "case#": self.data[str(server.id)]["case#"],
            "cases": self.data[str(server.id)]['cases']
        }}}
        self.col.update_one({"auth": True}, document)
        await ctx.send(F"{self.bot.check} Successfully edited the case number **{case_number}**!")
            

    @modlog.command(description="See all of the current configurations for the server modlog.", aliases=['set', 'configurations'], usage=['modlog settings'])
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not str(server.id) in self.data:
            return await ctx.send(f"{self.bot.x} I can't find any current configurations for your server! Use the command `{self.bot.prefix}modlog` to see the modlog commands.")
        modlog = self.data[str(server.id)]["status"]
        if modlog == "disabled":
            modlog_toggled = f"{self.bot.x} Modlog is disabled."
        else:
            modlog_toggled = f"{self.bot.check} Modlog is enabled."
        modlog_chan = server.get_channel(int(self.data[str(server.id)]["channel"]))
        if not modlog_chan:
            modlog_chan = "Channel is not found or set."
        else:
            modlog_chan = modlog_chan.mention
        embed = discord.Embed(color=self.bot.embed)
        embed.set_author(name=f"{server.name}", icon_url=server.icon_url)
        embed.add_field(name="Modlog", value=modlog_toggled, inline=False)
        embed.add_field(name="Modlog Channel", value=modlog_chan, inline=False)
        embed.add_field(name="Modlog Cases", value=self.data[str(server.id)]['case#'], inline=False)
        await ctx.send(embed=embed)

    @commands.command(description="Kick a user from the server.", aliases=['k'], usage=['kick @User <reason>', 'kick @Brendan Being awesome'])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member = None, *, reason = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not user:
            return await ctx.send(f"{self.bot.x} I don't think you wanna kick yourself? So lets just specify a member :smile:")
        if user == ctx.author:
            return await ctx.send(F"{self.bot.x} Congratulations, you played yourself.")
        if user.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
            if ctx.author == server.owner:
                pass
            else:
                await ctx.send(f"{self.bot.x} This user is equal or higher than your current role position.")
                return
        try:
            await user.send(f"Hello. You have been kicked from **{server}** for the reason of:\n{reason}")
        except discord.Forbidden:
            pass 
        try:
            await user.kick(reason=f"{ctx.author} - {reason}")
        except discord.Forbidden:
            return await ctx.send(f"{self.bot.x} I was unable to kick that user. Please check if I am below that user or if I don't have `kick_members` permission.")
        await ctx.send(f"`Case #{self.data[str(server.id)]['case#'] + 1}` Successfully kicked **{user}**!")
        await self.send_log(ctx, user, reason, "Kick")

    @commands.command(description="Ban a user from the server.", aliases=['b'], usage=['ban @User <reason>', 'ban @Brendan Being awesome'])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member = None, *, reason = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not user:
            return await ctx.send(f"{self.bot.x} I don't think you wanna ban yourself? So lets just specify a member :smile:")
        if user == ctx.author:
            return await ctx.send(F"{self.bot.x} Congratulations, you played yourself.")
        if user.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
            if ctx.author == server.owner:
                pass
            else:
                await ctx.send(f"{self.bot.x} This user is equal or higher than your current role position.")
                return
        try:
            await user.send(f"Hello. You have been banned from **{server}** for the reason of:\n{reason}")
        except discord.Forbidden:
            pass 
        try:
            await user.ban(reason=f"{ctx.author} - {reason}")
        except discord.Forbidden:
            return await ctx.send(f"{self.bot.x} I was unable to ban that user. Please check if I am below that user or if I don't have `ban_members` permission.")
        await ctx.send(f"`Case #{self.data[str(server.id)]['case#'] + 1}` Successfully banned **{user}**!")
        await self.send_log(ctx, user, reason, "Ban")

    @commands.command(description="Ban a user from the server, then unban them. Clearing all of there messages for the past 2 days.", aliases=['sb'], usage=['softban @User <reason>', 'softban @Brendan Being awesome'])
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, user: discord.Member = None, *, reason = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not user:
            return await ctx.send(f"{self.bot.x} I don't think you wanna softban yourself? So lets just specify a member :smile:")
        if user == ctx.author:
            return await ctx.send(F"{self.bot.x} Congratulations, you played yourself.")
        if user.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
            if ctx.author == server.owner:
                pass
            else:
                await ctx.send(f"{self.bot.x} This user is equal or higher than your current role position.")
                return
        try:
            await user.send(f"Hello. You have been softbanned from **{server}** for the reason of:\n{reason}")
        except discord.Forbidden:
            pass 
        try:
            await user.ban(reason=f"{ctx.author} - {reason}")
            await user.unban(reason=f"Automatic unban.")
        except discord.Forbidden:
            return await ctx.send(f"{self.bot.x} I was unable to softban that user. Please check if I am below that user or if I don't have `ban_members` permission.")
        await ctx.send(f"`Case #{self.data[str(server.id)]['case#'] + 1}` Successfully softbanned **{user}**!")
        await self.send_log(ctx, user, reason, "Softban")
    
    @commands.command(description="Unban a user, allow them to join back wtihout having a expired invite.", aliases=['ub'], usage=['unban @User <reason>', 'unban @Brendan Was annoying me, so I had to unban!'])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user, *, reason = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        user = await arg.get_member(ctx, user)
        if not user:
            return await ctx.send(F"{self.bot.x} That is an invalid user.")
        if user == ctx.author:
            return await ctx.send(f"{self.bot.x} If you are banned, how are you able to type in chat?")
        i = 0
        n = 0 
        try:
            await server.fetch_ban(user)
        except discord.errors.NotFound:
            return await ctx.send(f"{self.bot.x} That user is not found in the banned list.")
        try:
            await server.unban(user, reason=f"{ctx.author} - {reason}")
        except discord.Forbidden:
            return await ctx.send(f"{self.bot.x} I am unable to unban that user. Please check my permissions, I need `ban_members` permission.")
        await ctx.send(F"`Case #{self.data[str(server.id)]['case#'] + 1}` Successfully unbanned **{user}**!")
        await self.send_log(ctx, user, reason, "Unban")
    
    @commands.group(aliases=['mutedrole'])
    @commands.has_permissions(manage_roles=True)
    async def muterole(self, ctx):
        prefix = "-"
        if not ctx.invoked_subcommand:
            embed = discord.Embed(color=self.bot.embed)
            embed.set_author(name=ctx.guild, icon_url=ctx.guild.icon_url)
            embed.add_field(name=f"{prefix}muterole create <muted_role>", value=f"""
            Creates a new role, removes the `send_messages` permission and `add_reactions` permission through every channel.
            """)
            embed.add_field(name=f"{prefix}muterole set <muted_role>", value=f"""
            Sets the muted role for the server. This will make it to where it to where no one can speak.
            """)
            await ctx.send(embed=embed)
    
    @muterole.command(description="Create a muted role disabling `send_messages` and `add_reactions` for every channel.", aliases=['c'], usage=['muterole create <mute-role>', 'muterole create Muted'])
    @commands.has_permissions(manage_roles=True)
    async def create(self, ctx, role = None):
        self.data = self.settings.find_one()
        server = ctx.guild 
        if not role:
            return await ctx.send(F"{self.bot.x} You need to specify the role you would like to create.")
        try:
            muted = await server.create_role(name=role)
        except discord.Forbidden:
            return await ctx.send(F"{self.bot.x} Oh no! I am unable to create this role, pleae check if I have the `manage_roles` permission. This permission will allow me to add and create roles.")
        chans = 0
        try:
            for p in server.channels:
                await p.set_permissions(muted, send_messages = False, add_reactions = False)
        except discord.Forbidden:
            await ctx.send(F"{self.bot.x} I am unable to set `send_messages` and `add_reactions` permissions for each channel. I believe the permission that I don't have is `manage_channels`. This permission allows me to edit, delete, and create channels in your server.")
        if not str(server.id) in self.data:
            data = {"$set": {str(server.id):{
                "muted-role": muted.id,
                "prefix": "-",
                "bypass-role": "not set",
                "ignored-channels": []
            }}}
            self.settings.update_one({"auth": True}, data)
            await ctx.send(f"{self.bot.check} Successfully created the muted role. I have set these permissions in **{len(server.channels)}** channels:\n`send_messsages` **|** {self.bot.x}\n`add_reactions` **|** {self.bot.x}")
        data = {"$set": {str(server.id):{
            "muted-role": muted.id,
            "prefix": self.data[str(server.id)]['prefix'],
            "bypass-role": self.data[str(server.id)]['bypass-role'],
            "ignored-channels": self.data[str(server.id)]['ignored-channels']
        }}} 
        self.settings.update_one({"auth": True}, data)
        await ctx.send(f"{self.bot.check} Successfully created the muted role. I have set these permissions in **{len(server.channels)}** channels:\n`send_messsages` **|** {self.bot.x}\n`add_reactions` **|** {self.bot.x}")

    @muterole.command(description="Set the mute role for your server. This role will be used for muting purposes.", aliases=['s'], usage=['muterole set @Muted', 'muterole set @Role or role'])
    @commands.has_permissions(manage_roles=True)
    async def set(self, ctx, *, role: discord.Role = None):
        self.data = self.settings.find_one()
        server = ctx.guild 
        if not role:
            return await ctx.send(F"{self.bot.x} You need to specify the role you would like to set as the muted role. You can mention the role, say the role id, or say the role name.")
        if not str(server.id) in self.data:
            data = {"$set": {str(server.id):{
                "muted-role": role.id,
                "prefix": "-",
                "bypass-role": "not set",
                "ignored-channels": []
            }}}
            self.settings.update_one({"auth": True}, data)
            await ctx.send(F"{self.bot.check} Successfully set the muted role to: {role.mention}")
        data = {"$set": {str(server.id):{
            "muted-role": role.id,
            "prefix": self.data[str(server.id)]['prefix'],
            "bypass-role": self.data[str(server.id)]['bypass-role'],
            "ignored-channels": self.data[str(server.id)]['ignored-channels']
        }}} 
        self.settings.update_one({"auth": True}, data)
        await ctx.send(F"{self.bot.check} Successfully set the muted role to: {role.mention}")

    @commands.command(description="Mute a user for a certain amount of time. If you don't specify a time, it will automatically set the time to 1 hour.", aliases=['m'], usage=['mute @User [time] [reason]', 'mute @Brendan 20h Interrupting our bonding session!'])
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, user: discord.Member = None, lmt: typing.Optional[convtime] = None, *, reason = None):
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
        self.data = self.col.find_one()
        self.set = self.settings.find_one()
        self.mutes = self.muted.find_one()
        time_str = " ".join((f'{y} {x}' for x,y in vars().items() if x in ('days','hours','minutes','seconds') if y > 0))
        if not user:
            return await ctx.send(f"{self.bot.x} You need to specify a user to mute.")
        if user == ctx.author:
            return await ctx.send(F"{self.bot.x} You can't mute yourself!")
        if user.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
            if ctx.author == server.owner:
                pass
            else:
                await ctx.send(f"{self.bot.x} This user is equal or higher than your current role position.")
                return
        if not str(server.id) in self.set:
            return await ctx.send(f"{self.bot.x} Hey! You don't have a muted role set for this server. If you already have one then use the command `{self.get_prefix(ctx.guild)}muterole set @Role`! If you don't have one then use the command `{self.get_prefix(ctx.guild)}muterole create Muted`.")
        muted = server.get_role(self.set[str(server.id)]['muted-role'])
        if not muted:
            return await ctx.send(F"{self.bot.x} Hey! You don't have a muted role set for this server. If you already have one then use the command `{self.get_prefix(ctx.guild)}muterole set @Role`! If you don't have one then use the command `{self.get_prefix(ctx.guild)}muterole create Muted`.")
        if muted in user.roles:
            return await ctx.send(f"{self.bot.x} That user is already muted.")
        try:
            await user.send(F"Hello! You have been muted in **{server.name}** for the reason of:\n{reason}")
        except discord.Forbidden:
            pass
        try:
            await user.add_roles(muted)
        except discord.Forbidden:
            return await ctx.send(f"{self.bot.x} Oh no! I am unable to mute this user, pleae check if I have the `manage_roles` permission. This permission will allow me to add and create roles.")
        await ctx.send(F"`Case #{self.data[str(server.id)]['case#'] + 1}` Successfully muted **{user}** for **{time_str}**.")
        await self.send_log(ctx, user, reason, "Mute", time_str)
        if not str(server.id) in self.mutes:
            doc = {"$set": {str(server.id):{
                "muted": {
                    str(user.id): {
                        "muted-time": time_str,
                        "mod": str(ctx.author.id),
                        "reason": reason
                    }
                }
            }}}
            self.muted.update_one({"auth": True}, doc)
        else:
            muted_list = self.mutes[str(server.id)]["muted"]
            doc = {"$set": {str(server.id):{
                "muted": {**muted_list, str(user.id):{
                    "muted-time": time_str,
                    "mod": str(ctx.author.id),
                    "reason": reason
                }}
            }}}
            self.muted.update_one({"auth": True}, doc)
        await asyncio.sleep(lmt)
        muted_list = self.mutes[str(server.id)]['muted']
        doc = {"$set": {str(server.id):{
            "muted": {k:v for k,v in muted_list.items() if k != str(user.id)}
        }}}
        self.muted.update_one({"auth": True}, doc)
        if muted in user.roles:
            await user.remove_roles(muted)
        else:
            return

    @commands.command(description="See all of the muted users in the server.", aliases=['ml', 'muted'], usage="mutedlist")
    @commands.has_permissions(manage_guild=True)
    async def mutedlist(self, ctx):
        self.data = self.muted.find_one()
        server = ctx.guild 
        if not str(server.id) in self.data:
            return await ctx.send(f"{self.bot.x} Your server doesn't have any muted users.")
        if not "muted" in self.data[str(server.id)]:
            return await ctx.send(F"{self.bot.x} Sorry, but there was an error! It appears to be that you don't have any muted members in the database.")
        muted_list = self.data[str(server.id)]["muted"]
        if muted_list == {}:
            return await ctx.send(f"No one is muted in this server.")
        users = [f"{server.get_member(int(x)).mention} - `{y['muted-time']}`\n `Mod`: **{server.get_member(int(y['mod']))}**" if y else f"{x}" for x,y in muted_list.items()]
        formatted = [f"**{x}**. {y}" for x,y in enumerate(users, start=1)]
        embed = discord.Embed(color=self.bot.embed)
        embed.set_author(name="Server muted members")
        embed.description = "\n".join(formatted)
        await ctx.send(embed=embed)

    @commands.command(description="Get the information on why the user was muted.", aliases=['mi'], usage="mutedinfo @User")
    @commands.has_permissions(manage_channels=True)
    async def mutedinfo(self, ctx, user: discord.Member = None):
        self.data = self.muted.find_one()
        server = ctx.guild 
        if not user:
            return await ctx.send(f"{self.bot.x} You need to specify the user you would like to see.")
        if not str(server.id) in self.data:
            return await ctx.send(f"{self.bot.x} That user is not muted.")
        muted_list = self.data[str(server.id)]["muted"]
        if not str(user.id) in muted_list:
            return await ctx.send(f"{self.bot.x} That user is not muted.")
        embed = discord.Embed(color=self.bot.embed)
        embed.set_author(name=user, icon_url=user.avatar_url)
        mod = await self.bot.fetch_user(int(muted_list[str(user.id)]["mod"]))
        embed.description = f"""
        **Moderator:** {mod} `{mod.id}`
        **Time Muted:** {muted_list[str(user.id)]["muted-time"]}
        **Reason:** {muted_list[str(user.id)]["reason"]}
        """
        await ctx.send(embed=embed)

    @commands.command(description="Remove the muted role from the user. Allowing them to access chats and to speak in them.", aliases=['um', 'un'], usage=['unmute @User [reason]', 'unmute @Brendan Confessed that he was setup!'])
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, user: discord.Member = None, *, reason = None):
        self.set = self.settings.find_one()
        self.data = self.col.find_one()
        self.mutes = self.muted.find_one()
        server = ctx.guild 
        if not user:
            return await ctx.send(F"{self.bot.x} You need to specify a user to unmute.")
        if user == ctx.author:
            return await ctx.send(f"{self.bot.x} You can't unmute yourself.")
        if not str(server.id) in self.data:
            return await ctx.send(F"{self.bot.x} Hey! You don't have a muted role set for this server. If you already have one then use the command `{self.get_prefix(ctx.guild)}muterole set @Role`! If you don't have one then use the command `{self.get_prefix(ctx.guild)}muterole create Muted`.")
        muted = server.get_role(self.set[str(server.id)]['muted-role'])
        if not muted:
            return await ctx.send(F"{self.bot.x} Hey! You don't have a muted role set for this server. If you already have one then use the command `{self.get_prefix(ctx.guild)}muterole set @Role`! If you don't have one then use the command `{self.get_prefix(ctx.guild)}muterole create Muted`.")
        if not muted in user.roles:
            return await ctx.send(f"{self.bot.x} That user isn't muted.")
        try:
            await user.remove_roles(muted)
        except discord.Forbidden:
            return await ctx.send(f"{self.bot.x} Oh no! I am unable to unmute this user, pleae check if I have the `manage_roles` permission. This permission will allow me to add and create roles.")
        await ctx.send(f"`Case #{self.data[str(server.id)]['case#'] + 1}` Successfully unmuted **{user}**!")
        await self.send_log(ctx, user, reason, "Unmute")
        muted_list = self.mutes[str(server.id)]["muted"]
        doc = {"$set": {str(server.id):{
            "muted": {k:v for k,v in muted_list.items() if k != str(user.id)}
        }}}
        self.muted.update_one({"auth": True}, doc)

    @commands.command(description="Ban a user for a certain a period of time. After the time is up it will automatically unban them.", aliases=['tb', 'temp'], usage=[''])
    @commands.has_permissions(ban_members=True)
    async def tempban(self, ctx, user: discord.Member = None, lmt: typing.Optional[convtime] = None, *, reason = None):
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
        self.data = self.col.find_one()
        time_str = " ".join((f'{y} {x}' for x,y in vars().items() if x in ('days','hours','minutes','seconds') if y > 0))
        if not user:
            return await ctx.send(f"{self.bot.x} You need to specify the user you would like to tempban.")
        if user == ctx.author:
            return await ctx.send(f"{self.bot.x} You can't tempban yourself!")
        if user.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
            if ctx.author == server.owner:
                pass
            else:
                await ctx.send(f"{self.bot.x} This user is equal or higher than your current role position.")
                return
        try:
            await user.send(f"Hello. You have been tempbanned from **{server}** for the reason of:\n{reason}")
        except discord.Forbidden:
            pass 
        try:
            await user.ban(reason=f"{ctx.author} - {reason}")
        except discord.Forbidden:
            return await ctx.send(f"{self.bot.x} I was unable to ban that user. Please check if I am below that user or if I don't have `ban_members` permission.")
        await ctx.send(F"`Case #{self.data[str(server.id)]['case#'] + 1}` Successfully tempbanned **{user}** for **{time_str}**.")
        await self.send_log(ctx, user, reason, "Tempban", time_str)
        await asyncio.sleep(lmt)
        try:
            await server.fetch_ban(user)
        except discord.errors.NotFound:
            return 
        await user.unban(reason=f"Auto-Unban, tempbanned by {ctx.author}")

    @commands.command(description="Warn them for breaking the rules.", aliases=["w"], usage=['warn @User [reason]', 'warn @Brendan Breaking rule #1'])
    @commands.has_permissions(manage_roles=True)
    async def warn(self, ctx, user: discord.Member = None, *, reason = None):
        server = ctx.guild 
        if not user:
            return await ctx.send(f"{self.bot.x} You need to specify the user you would like to warn.")
        if user == ctx.author:
            return await ctx.send(f"{self.bot.x} You can't warn yourself!")
        if user.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
            if ctx.author == server.owner:
                pass
            else:
                await ctx.send(f"{self.bot.x} This user is equal or higher than your current role position.")
                return
        if user.bot:
            return await ctx.send(f"{self.bot.x} You can't warn a bot!")
        await self.warn_user(ctx, user, reason)

    @commands.command(description="See all of the warnings for a certain user.", aliases=['warns'], usage=['warnings @User'])
    @commands.has_permissions(manage_channels=True)
    async def warnings(self, ctx, user: discord.Member = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not user:
            user = ctx.author
        if not str(server.id) in self.data:
            return await ctx.send(f"{self.bot.x} That user doesn't have any warnings.")
        
        cases = self.data[str(server.id)]["cases"]
        found_cases = [c for c in cases if c["user"] == str(user.id)]
        found_warns = [c for c in found_cases if c["action"] == "Warn"]
        if len(found_cases) == 0 or len(found_warns) == 0:
            return await ctx.send(f"{self.bot.x} That user doesn't have any warnings.")
        
        embed = await self.embed_mk(ctx, found_warns[:8], user)
        message = await ctx.send(embed=embed)
        if len(found_warns) > 8:
            await message.add_reaction("◀")
            await message.add_reaction("❌")
            # await message.add_reaction("🇮")
            await message.add_reaction("▶")
        def reactioncheck(reaction, user):
            if user == ctx.author:
                if reaction.message.id == message.id:
                    if reaction.emoji == "▶" or reaction.emoji == "❌" or reaction.emoji == "◀" or reaction.emoji == "🇮":
                        return True
        x = 0
        while True:
            reaction, user2 = await self.bot.wait_for("reaction_add", check=reactioncheck)
            if reaction.emoji == "◀":
                x -= 8
                if x < 0:
                    x = 0
                await message.remove_reaction("◀", user2)
            elif reaction.emoji == "❌":
                await message.delete()
            # elif reaction.emoji == "🇮":
            #     embed = discord.Embed(color=self.bot.embed)
            #     embed.set_author(name=user3 , icon_url=user3.avatar_url)
            #     embed.description = f"""
            #     **Total Cases**: {len(found_cases)}
            #     **Total Warns:** {len(found_warns)}
            #     **Total Kicks:** {len(found_kicks)}
            #     **Total Softbans:** {len(found_softbans)}
            #     **Total Bans:** {len(found_bans)}
            #     **Total Unbans:** {len(found_unbans)}
            #     """
            #     await message.edit(embed=embed)
            #     await message.add_reaction("◀")
            #     await message.remove_reaction("🇮", user3)
            elif reaction.emoji == "▶":
                x += 8
                if x > len(found_cases):
                    x = len(found_cases) - 8
            embed = await self.embed_mk(ctx, found_warns[x:x+8], user)
            await message.edit(embed=embed)
            await message.remove_reaction("▶", user2)

    @commands.command(description="You remove a warn from the database.", aliases=["rm"], usage=['removewarn #', 'removewarn 42'])
    @commands.has_permissions(manage_roles=True)
    async def removewarn(self, ctx, case_number: int = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not case_number:
            return await ctx.send(f"{self.bot.x} You need to specify the warn you want to remove.")
        if not str(server.id) in self.data:
            return await ctx.send(f"{self.bot.x} Your server doesn't have any warnings.")
        cases = self.data[str(server.id)]["cases"]
        found_case = [c for c in cases if c['id'] == case_number]
        if len(found_case) == 0:
            return await ctx.send(F"{self.bot.x} I couldn't find a case with that id number.")
        case = found_case[0]
        if case['action'] == "Warn":
            cases.remove(case)
            document = {"$set": {str(server.id):{
                "channel": self.data[str(server.id)]["channel"],
                "status": self.data[str(server.id)]["status"],
                "case#": self.data[str(server.id)]["case#"],
                "cases": self.data[str(server.id)]['cases']
            }}}
            self.col.update_one({"auth": True}, document)
            await ctx.send(f"{self.bot.check} Removed the warning **#{case_number}** successfully!")
        else:
            return await ctx.send(f"{self.bot.x} That case is not a warning, that case is a **{case['action']}**.")

    @commands.command(description="Clear every warning a user has been given.", aliases=['clearwarn', 'clw'], usage=['clearwarns @User', 'clearwarns @Brendan'])
    @commands.has_permissions(manage_roles=True)
    async def clearwarns(self, ctx, user: discord.Member = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        perms = ctx.channel.permissions_for(ctx.author).manage_nicknames
        if not str(server.id) in self.data:
            return await ctx.send(f"{self.bot.x} Your server doesn't have any warnings.")
        cases = self.data[str(server.id)]["cases"]
        found_cases = [c for c in cases if c['user'] == str(user.id)]
        found_warns = [c for c in found_cases if c["action"] == "Warn"]
        for warn in found_warns:
            cases.remove(warn)
            document = {"$set": {str(server.id):{
                "channel": self.data[str(server.id)]["channel"],
                "status": self.data[str(server.id)]["status"],
                "case#": self.data[str(server.id)]["case#"],
                "cases": self.data[str(server.id)]['cases']
            }}}
            self.col.update_one({"auth": True}, document)
        await ctx.send(f"{self.bot.check} Removed all of the users warning successfully!")

    
    @commands.command(description="Locks down a channel so no one can speak in it at the current time using the command again will unlock it.", aliases=['lock'], usage=['lockdown #channel <duration>', 'lockdown #general 30m'])
    @commands.has_permissions(manage_guild=True)
    async def lockdown(self, ctx, channel: discord.TextChannel = None, lmt: typing.Optional[convtime] = None):
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
        if not channel:
            channel = ctx.channel 
        try:
            if channel.overwrites_for(ctx.guild.default_role).send_messages == True or channel.overwrites_for(ctx.guild.default_role).send_messages == None:
                overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = False
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
                await ctx.send(f"{self.bot.check} Successfully locked down {channel.mention} for **{time_str}**.")
            else:
                overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
                overwrite.send_messages = None
                await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
                await ctx.send(f"{self.bot.check} Successfully unlocked {channel.mention}")
        except:
            await ctx.send(f"{self.bot.x} I am unable to edit those channel permissions.")

    @commands.command(description="Ban multiple users at a time.", aliases=['mb', 'massb'], usage=['massban @User @User', 'massban @Brendan @Anish @Father. @Teddy'])
    @commands.has_permissions(ban_members=True)
    async def massban(self, ctx, users: commands.Greedy[discord.Member] = None, *, reason = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not users:
            return await ctx.send(f"{self.bot.x} You need to specify a user or users to ban.")
        for user in users:
            if user.top_role.position >= ctx.author.top_role.position and ctx.author != ctx.guild.owner:
                if ctx.author == server.owner:
                    pass
                else:
                    await ctx.send(f"{self.bot.x} One or all of the users you have mentioned are higher or equal to your role position.")
                    
            try:
                await user.ban(reason=f"{ctx.author} - {reason}")
            except discord.Forbidden:
                return await ctx.send(F"{self.bot.x} I can't ban that user. Please check if I have the `ban_members` permission.")
            await self.send_log(ctx, user, reason, "Ban")
        banned = ", ".join(x.name for x in users)
        await ctx.send(f"Successfully banned **{banned}**.")
	
	
	
	
def setup(bot):
    bot.add_cog(Moderation(bot))
