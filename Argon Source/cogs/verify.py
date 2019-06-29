import discord 
from discord.ext import commands 
from pymongo import MongoClient as mcl 
import random 
from utils import arg
import asyncio
from datetime import datetime 

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.client = mcl("mongodb://o:o99999@ds337377.mlab.com:37377/modtest")
        self.db = self.client['modtest']
        self.col = self.db['verification']

    @commands.group(aliases=['verification'])
    @commands.has_permissions(manage_guild=True)
    async def verified(self, ctx):
        if not ctx.invoked_subcommand:
            embed = discord.Embed(color=self.bot.embed)
            embed.set_author(name=ctx.guild, icon_url=ctx.guild.icon_url)
            embed.add_field(name="-verified role @role", value=f"""
            The role that will be given to users when they enter the server. (Removed when they complete verification)       
            """)
            embed.add_field(name=f"-verified after @role", value=f"""
            The role that will be given to users when the complete verification.
            """)
            embed.add_field(name=f"-verified send #channel <message>", value=f"""
            Sends the message specified in the channel specified 
            """)
            embed.add_field(name=f"-verified logging #channel", value=f"""
            Where to log successfull verification.
            """)
            await ctx.send(embed=embed)

    @verified.command(description="Setup a role that is given to a user once they enter the server. Kind of like auto role!", aliases=['r'], usage=['verified role @role', 'verified role @New Comer'])
    @commands.has_permissions(manage_guild=True)
    async def role(self, ctx, *, role: discord.Role = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not role:
            return await ctx.send(f"{self.bot.x} You need to specify the role you would like to add to the user once he/she joins the server.")
        if not str(server.id) in self.data:
            data = {"$set": {str(server.id):{
                "newrole": role.id,
                "afterole": "not set",
                "logging": "not set",
                "message-channel": 'not set'
            }}}
            self.col.update_one({"auth": True}, data)
            await ctx.send(F"{self.bot.check} Successfully set the new comer role to: {role.mention}")
        data = {"$set": {str(server.id):{
            "newrole": role.id,
            "afterole": self.data[str(server.id)]['afterole'],
            "logging": self.data[str(server.id)]['logging'],
            "message-channel": self.data[str(server.id)]['message-channel']
        }}}
        self.col.update_one({"auth": True}, data)
        await ctx.send(F"{self.bot.check} Successfully set the new comer role to: {role.mention}")

    @role.error 
    async def role_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"{self.bot.x} I could not find that role. Make sure that the role is still on the server.")

    @verified.command(description="Set the role that will be added to the user when he/she passes the verification.", aliases=['ater'], usage=['verified after @role', 'verified after @New Comer'])
    @commands.has_permissions(manage_guild=True)
    async def after(self, ctx, *, role: discord.Role = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not role:
            return await ctx.send(f"{self.bot.x} You need to specify the role you would like to add to the user once he/she finishes the verification.")
        if not str(server.id) in self.data:
            data = {"$set": {str(server.id):{
                "newrole": "not set",
                "afterole": role.id,
                "logging": "not set",
                "message-channel": 'not set'
            }}}
            self.col.update_one({"auth": True}, data)
            await ctx.send(F"{self.bot.check} Successfully set the verified role to: {role.mention}")
        data = {"$set": {str(server.id):{
            "newrole": self.data[str(server.id)]['newrole'],
            "afterole": role.id,
            "logging": self.data[str(server.id)]['logging'],
            "message-channel": self.data[str(server.id)]['message-channel']
        }}}
        self.col.update_one({"auth": True}, data)
        await ctx.send(F"{self.bot.check} Successfully set the verified role to: {role.mention}")

    @after.error 
    async def after_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"{self.bot.x} I could not find that role. Make sure that the role is still on the server.")

    @verified.command(description="Send a message to a certain channel so that when the user joins the server he/she will know what to do.", aliases=['s'], usage=['verified send #channel <message>', 'verified send #holdup Please use the command `-verify` to join the server!'])
    @commands.has_permissions(manage_guild=True)
    async def send(self, ctx, channel: discord.TextChannel = None, *, message = None):
        server = ctx.guild 
        if not channel:
            channel = ctx.channel 
        if not message:
            return await ctx.send(f"{self.bot.x} You need to specify the message you would like to me to send in {channel.mention}")
        if not str(server.id) in self.data:
            data = {"$set": {str(server.id):{
                "newrole": "not set",
                "afterole": "not set",
                "logging": "not set",
                "message-channel": channel.id
            }}}
            self.col.update_one({"auth": True}, data)
            await channel.send(message)
            await ctx.send(F"{self.bot.check} Successfully sent that message to: {channel.mention}")
        data = {"$set": {str(server.id):{
            "newrole": self.data[str(server.id)]['newrole'],
            "afterole": self.data[str(server.id)]['afterole'],
            "logging": self.data[str(server.id)]['logging'],
            "message-channel": channel.id
        }}}
        self.col.update_one({"auth": True}, data)
        await channel.send(message)
        await ctx.send(F"{self.bot.check} Successfully sent that message to: {channel.mention}")
        

    @verified.command(description="See the actions of the users. If a user gets denied it will log into this channel, if the user does the verification correctly it will log the success message of the user.", aliases=['logs'], usage=['verified logging #channel', 'verified logging #verified-logs'])
    @commands.has_permissions(manage_guild=True)
    async def logging(self, ctx, *, channel: discord.TextChannel = None):
        self.data = self.col.find_one()
        server = ctx.guild 
        if not channel:
            channel = ctx.channel 
        if not str(server.id) in self.data:
            data = {"$set": {str(server.id):{
                "newrole": "not set",
                "afterole": "not set",
                "logging": channel.id,
                "message-channel": 'not set'
            }}}
            self.col.update_one({"auth": True}, data)
            await ctx.send(f"{self.bot.check} Successfully set the verified logging channel to: {channel.mention}")
        data = {"$set": {str(server.id):{
            "newrole": self.data[str(server.id)]['newrole'],
            "afterole": self.data[str(server.id)]['afterole'],
            "logging": channel.id,
            "message-channel": self.data[str(server.id)]['message-channel']
        }}}
        self.col.update_one({"auth": True})
        await ctx.send(f"{self.bot.check} Successfully set the verified logging channel to: {channel.mention}")


    @commands.command(description="Allows a user to access the channels.")
    async def verify(self, ctx):
        self.data = self.col.find_one()
        server = ctx.guild
        if not str(server.id) in self.data:
            return
        msg_chan = server.get_channel(self.data[str(server.id)]['message-channel'])
        if not msg_chan:
            pass
        msg = await ctx.send(F"{ctx.author.mention} Check your dms for the verification!")
        await ctx.message.delete()
        await asyncio.sleep(1)
        await msg.delete()
        logs = server.get_channel(self.data[str(server.id)]['logging'])
        if not logs:
            pass 
        n1=random.randint(1,11)
        n2=random.randint(1,11)
        
        add=n1+n2
        embed = discord.Embed(color=self.bot.embed)
        embed.add_field(name="Verification", value=f"""
        To access the server you will need to solve a math equation. You will say this equation below.
        **What is {str(n1)}+{str(n2)}=?**
        """)
        await ctx.author.send(embed=embed)
        def check(m):
            return m.author==ctx.message.author
        msg = await self.bot.wait_for('message', check=check)
        if str(msg.content) != str(add):
            await ctx.author.send(F"You have failed the varification. Please reverify using the `-verify` command.")
            embed = discord.Embed(color=0xFA8072, timestamp=datetime.utcnow())
            embed.title = "Verification Unsuccessful!"
            embed.description = f"""
            User failed verification.
            
            **User:** {ctx.author} {ctx.author.mention}
            **Equation:** {n1}+{n2}={msg.content}
            """
            await logs.send(embed=embed)
        else:
            await ctx.author.send(f"Congratulations! You have correctly done the verification. Have fun in **{server}**!")
            role1 = server.get_role(self.data[str(server.id)]['afterole'])
            if not role1:
                role = "Role not found or not set."
            else:
                role = role1.mention
            try:
                await ctx.author.add_roles(role1)
            except discord.Forbidden:
                role = "Couldn't give the new role because I don't have permissions."
            before1 = server.get_role(self.data[str(server.id)]['newrole'])
            if not before1:
                before = "Role not found or not set."
            else:
                before = before1.mention
            try:
                await ctx.author.remove_roles(before1)
            except discord.Forbidden:
                role = "Couldn't give the new role because I don't have permissions."
            embed = discord.Embed(color=0x00FF7F, timestamp=datetime.utcnow())
            embed.title = "Verification Successful!"
            embed.description = f"""
            User passed verification!
            
            **User:** {ctx.author} {ctx.author.mention}
            **Equation:** {n1}+{n2}={msg.content}
            **Role Taken:** {before}
            **Role Given:** {role}
            """
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.data = self.col.find_one()
        server = member.guild 
        if not str(server.id) in self.data:
            return 
        role = server.get_role(self.data[str(server.id)]['newrole'])
        if not role:
            return
        logs = server.get_channel(self.data[str(server.id)]['logging'])
        if not logs:
            pass 
        await member.add_roles(role)
        embed = discord.Embed(color=self.bot.embed, timestamp=datetime.utcnow())
        embed.title = "Member Joined"
        embed.add_field(name="Proccessing", value=f"""
        I have added the {role.mention} role to them.
        They have to use the command `-verify` to continue accessing the server.
        """)
        await logs.send(embed=embed)
        

def setup(bot):
    bot.add_cog(Verification(bot))
