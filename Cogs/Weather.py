import discord, datetime
import requests, json, os
from bs4 import BeautifulSoup
from discord.ext import commands

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def weatherinfo(self, location):
        key = os.environ['weather']
        url = "http://api.openweathermap.org/data/2.5/forecast?q=" + location + "&cnt=10&units=metric&lang=kr&APPID=" + key

        html = requests.get(url).text
        data = json.loads(html)

        return data

    @commands.command()
    async def 날씨(self, ctx):
        """Show you weather info
        
        Insert your correct location.
        해운대 -> X
        해운대구 -> O
        """
        place = '지역을 입력하세요'
        request_e = discord.Embed(title="날씨 검색", description=place, color=0xcceeff)
        await ctx.send(embed=request_e)
        await ctx.message.delete()
        location1 = await self.bot.wait_for('message', timeout=15.0)
        location = str(location1.content)
        await location1.delete()
        data = self.weatherinfo(location)

        name = data['city']['name']
        weather = data['list']

        print(name)

        for i in weather:
            embed = discord.Embed(title=location + ' 날씨 정보',
                                description=location + ' 날씨 정보입니다.',
                                colour=discord.Colour.gold())

            date = datetime.datetime.fromtimestamp(
            i['dt']).strftime('%Y-%m-%d %H:%M:%S')
            print("예보 시각: " + date)
            embed.add_field(name='예보 시각', value=date, inline=False)
            temp = i['main']['temp']
            print("기온: " + str(temp))
            embed.add_field(name='기온', value=temp, inline=False)
            feel = i['main']['feels_like']
            print("체감 기온: " + str(feel))
            embed.add_field(name='체감 기온', value=feel, inline=False)
            humidity = i['main']['humidity']
            print("습도: " + str(humidity))
            embed.add_field(name='습도', value=humidity, inline=False)
            cloud = i['weather'][0]['description']
            print("구름: " + cloud)
            embed.add_field(name='구름', value=cloud, inline=False)
            await ctx.send(embed=embed)
            print("=" * 20)

async def setup(bot):
    await bot.add_cog(Weather(bot))