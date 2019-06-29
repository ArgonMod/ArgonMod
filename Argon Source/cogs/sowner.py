import discord 
from discord.ext import commands 

class ServerOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @commands.command(name="kickbots",aliases=["botkick"],description="Kick all bots that are in the server.")
    async def kickbots(self, ct):
        if not ctx.guild:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} This is a server only command.")
        if not ctx.author==ctx.guild.owner:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Only the owner of the guild can use this command.")
        msg=await ctx.send("Kicking all bots..")
        count=0
        blist=""
        for user in ctx.guild.members:
            if user.bot and str(user)!="Argon Tester#0057":
                try:
                    await user.kick()
                    count+=1
                    if blist!="":
                        blist+=", "
                    blist+=str(user)
                except:
                    pass
        return await msg.edit(content=F"Success! {count} bots were kicked.\nThe following bots were kicked: {blist}")
    @commands.command(name="kickrole",aliases=["rolekick"],usage=["kickrole [@role]"],description="Kick all the users that have the specified role in the server.")
    async def kickrole(self, ctx,arg:discord.Role = None):
        if not ctx.guild:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} This is a server only command.")
        if not ctx.author==ctx.guild.owner:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} Only the owner of the guild can use this command.")
        if not arg:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The proper usage of this command is {self.bot.prefix}kickrole [@role].")
        msg=await ctx.send(F"Kicking all users with the {arg} role.")
        count=0
        blist=""
        for user in ctx.guild.members:
            if arg in user.roles:
                try:
                    await user.kick()
                    count+=1
                    if blist!="":
                        blist+=", "
                    blist+=str(user)
                except:
                    pass
        return await msg.edit(content=F"Success! {count} users were kicked.\nThe following users were kicked: {blist}")
    @commands.command(name="lockrole",aliases=["rolelock"],usage=["lockrole [@role]"],description="Prevent all users with the role from speaking.")
    @commands.has_permissions(manage_roles=True)
    async def lockrole(self, ctx,arg:discord.Role = None):
        if not ctx.guild:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} This is a server only command.")
        if not arg:
            return await ctx.send(F"{self.bot.x}{ctx.author.mention} The proper usage of this command is {self.bot.prefix}lockrole [@role].")
        msg=await ctx.send(F"Muting all users with the {arg} role.")
        count=0
        blist=""
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(arg, read_messages=True,send_messages=False)
            if blist!="":
                blist+=", "
            blist+=str(channel.mention)
        return await msg.edit(content=F"Success! Anyone with the {arg.mention} role as there highest role cannot speak in the following channels: {blist}")
        
                               
        

def setup(bot):
    bot.add_cog(ServerOwner(bot))
