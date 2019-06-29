import re
import random
import asyncio
import aiohttp
import json
from discord import Game
from discord.ext import commands
from discord.ext.commands import Bot
import discord
import time
from discord.ext.commands import CommandNotFound
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
import os
from datetime import datetime, timedelta,date
import psutil
import random
from discord.utils import get

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @commands.command(usage=["embed hex color | Embed Title | Embed Description"],description="Make an amazing embed! The correct usage of this command is `{self.bot.prefix}embed hex color | Embed Title | Embed Description`")
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx, *, arg = None):
        '''Make an amazing embed! The correct usage of this command is `{self.bot.prefix}embed hex color | Embed Title | Embed Description`'''
        try:
            hexcode, title, description= arg.split("|")
        except:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention}The correct usage of this command is `{self.bot.prefix}embed hex color | Embed Title | Embed Description`.\nAn example is `{self.bot.prefix}embed #{self.bot.embed} | Insert Title | Insert Description`")
        
        try:
            color = int(hexcode[1:],16)
            if color > 0xffffff:
                raise ValueError
        except ValueError:
            color = self.bot.embed
        embed = discord.Embed(color=color)
        embed.title = title 
        embed.description = description
        return await ctx.send(embed=embed)
    
    @commands.command(name="serverinfo",description="Get info on your server.")
    async def serverinfo(self,ctx):
        embed=discord.Embed(description=str(ctx.message.guild)+"'s Current Member Count: "+str(ctx.message.guild.member_count)+" :tada:",color=0x008000,timestamp=datetime.utcnow() )
        return await ctx.send(embed=embed)
        
    @commands.command(name="userinfo",description="Get lots of info on any user",usage=["userinfo","userinfo [@user]"])
    async def userinfo(self, ctx, user:discord.Member=None):
        '''Get info on any user. Usage: !userinfo (@user)'''
        
        server = ctx.guild
        if not user:
            user = ctx.author
        joined_server = user.joined_at.strftime("%d %b %Y %H:%M")
        joined_discord = user.created_at.strftime("%d %b %Y %H:%M")
        if user.status == discord.Status.online:
            status="**Online**"
        if user.status == discord.Status.idle:
            status="**Idle**"
        if user.status == discord.Status.do_not_disturb:
            status="**Do Not Disturb**"
        if user.status == discord.Status.offline:
            status="**Offline**"
        description=""
        input = sorted([x for x in ctx.guild.members if x.joined_at], key=lambda x: x.joined_at).index(user) + 1
        if user.activity:
            if isinstance(user.activity, discord.Spotify):
                m, s = divmod(user.activity.duration.total_seconds(), 60)
                currentm, currents = divmod((datetime.utcnow() - user.activity.start).total_seconds(), 60)
                time_format = "%d:%02d"
                duration = time_format % (m, s)
                current = time_format % (currentm, currents)
                description = "Listening to [{} by {}](https://open.spotify.com/track/{}) `[{}/{}]`".format(user.activity.title, user.activity.artists[0], user.activity.track_id, current, duration)
            elif isinstance(user.activity, discord.Streaming):
                description="Streaming [{}]({})".format(user.activity.name, user.activity.url)
            else:
                description="{} {}{}".format(user.activity.type.name.title(), user.activity.name, (" for " + self.format_time_activity(datetime.now().timestamp() - (user.activity.timestamps["start"]/1000)) if hasattr(user.activity, "timestamps") and "start" in user.activity.timestamps else ""))
        roles=[x.mention for x in user.roles if x.name != "@everyone"][::-1][:20]
        s=discord.Embed(description=description, colour=user.colour, timestamp=datetime.utcnow())
        s.set_author(name=user.name, icon_url=user.avatar_url)
        s.set_thumbnail(url=user.avatar_url)
        s.add_field(name="Joined Discord", value=joined_discord)
        s.add_field(name="Joined {}".format(server.name), value=joined_server)
        s.add_field(name="Name", value="{}".format(user.name))
        s.add_field(name="Nickname", value="{}".format(user.nick))
        s.add_field(name="Discriminator", value=user.discriminator)
        s.add_field(name="Status", value="{}".format(status))
        s.add_field(name="User's Colour", value="{}".format(user.colour))
        s.add_field(name="User's ID", value="{}".format(user.id))
        s.add_field(name="Highest Role", value=user.top_role)
        s.add_field(name="Number of Roles", value=len(user.roles) - 1)
        print(3)
        if not roles:
            s.add_field(name="Roles", value="None", inline=False) 
        else:
            if len(user.roles) - 1 > 20:
                s.add_field(name="Roles", value="{}... and {} more roles".format(", ".join(roles), (len(user.roles) - 21)), inline=False) 
            else:
                s.add_field(name="Roles", value=", ".join(roles), inline=False)
        print(4)
        return await ctx.send(embed=s)

def setup(bot):
    bot.add_cog(Utility(bot))
