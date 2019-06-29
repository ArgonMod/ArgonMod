import discord 
from discord.ext import commands 

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    @commands.command(description="Get all of the commands the bot has.")
    async def help(self, ctx, command = None):
        if not command:
            embed = discord.Embed(color=self.bot.embed)
            embed.title = "Argon Help"
            embed.description = f"""
            `{self.bot.prefix}help <command>` - Show the information about a command
            """
            embed.add_field(name="Moderation", value=f"""
            `ban`, `kick`, `softban`, `tempban`, `unban`, `mute`, `unmute`, `mutedlist`, `mutedinfo`
            `mutedrole`, `warn`, `removewarn`, `clearwarns`,`lockrole`,`rolekick`,`botkick`
            """)
            embed.add_field(name=f"Utility", value=f"""
            `embed`,`serverinfo`,`userinfo`
            """, inline=False)
            embed.add_field(name=f"Verification", value=f"""
            `verified`, `verify`,`fastverify`
            """, inline=False)
            embed.add_field(name=f"AutoMod", value=f"""
            `automod`, `autorule`,`antispam`,`antiswear`
            """, inline=False)
            await ctx.author.send(embed=embed)
            await ctx.message.add_reaction('\U0001f4e7')
            return
        command_info = self.bot.get_command(command)
        if not command_info:
            return await ctx.send(f"{self.bot.x} That is not a registered command.")
        else:
            try:
                try:
                    if command_info.description == '':
                        description = "Command has no description."
                    else:
                        description = command_info.description
                except:
                    description = "Command has no description."
                try:
                    if command_info.aliases == []:
                        aliases = "There are no aliases for this command."
                    else:
                        aliases = ", ".join(command_info.aliases)
                except:
                    aliases = "There are no aliases for this command."
                try:
                    usage = "\n{self.bot.prefix}".join(command_info.usage)
                except:
                    usage=command_info
                embed = discord.Embed(color=self.bot.embed)
                embed.add_field(name=f"{command_info.cog_name} - {command_info.name}", value=f"""
                {description}
                """)
                embed.add_field(name="Aliases:", value=f"`{aliases}`", inline=False)
                embed.add_field(name="Usage:", value=f"`{self.bot.prefix}{usage}`", inline=False)
                await ctx.send(embed=embed)
            except:
                await ctx.send(F"{self.bot.x} Use the command `{self.bot.prefix}{command}` to see the commands it has.")
        
def setup(bot):
    bot.add_cog(Help(bot))
