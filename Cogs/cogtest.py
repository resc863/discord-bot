import discord
from discord import app_commands
from discord.ext import commands

class CogTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Weather ready")

    @app_commands.command(name="cogtest", description="test")
    @app_commands.describe(text="text")
    async def cogtest(self, interaction: discord.Interaction, text:str):
        """Show you weather info
        
        Insert your correct location.
        해운대 -> X
        해운대구 -> O
        """
        
        embed = discord.Embed(title='Test', description=text, colour=discord.Colour.gold())
            
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CogTest(bot))