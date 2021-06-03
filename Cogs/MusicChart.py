import discord, requests
from bs4 import BeautifulSoup
from discord.ext import commands, tasks

class MusicChart(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def 멜론(self, ctx):
		header = {
        		'User-Agent':
        		'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'
    		}
		melon = requests.get('https://www.melon.com/chart/index.htm', headers=header)  # 멜론차트 웹사이트
		html = melon.text
		parse = BeautifulSoup(html, 'html.parser')
		titles = parse.find_all("div", {"class": "ellipsis rank01"})
		songs = parse.find_all("div", {"class": "ellipsis rank02"})

		title = []
		song = []

		for t in titles:
			title.append(t.find('a').text)

		for s in songs:
			song.append(s.find('span', {"class": "checkEllipsis"}).text)

		embed = discord.Embed(title="멜론 실시간 차트", description="")

		for i in range(25):
			embed.add_field(name='%3d위: ' % (i + 1), value="%s - %s" % (title[i], song[i]), inline=False)

		await ctx.message.delete()
		await ctx.send(embed=embed)

		embed = discord.Embed(title="멜론 실시간 차트", description="")
		
		for i in range(25, 50):
			embed.add_field(name='%3d위: ' % (i + 1), value="%s - %s" % (title[i], song[i]), inline=False)

		await ctx.send(embed=embed)

	@commands.command()
	async def 빌보드(self, ctx):
		url = 'https://www.billboard.com/charts/hot-100'
		html = requests.get(url)
		soup = BeautifulSoup(html.text, 'html.parser')
		sp = soup.find_all('span', {
			'class':
			'chart-element__information__song text--truncate color--primary'
    	})

		sp1 = soup.find_all(
			'span', {
				'class':
				'chart-element__information__artist text--truncate color--secondary'
			})

		embed = discord.Embed(title="BillBoard Top 100 Lists", description="")

		for i in range(25):
			embed.add_field(name='%3d위: ' % (i + 1), value="%s - %s" % (sp[i].string, sp1[i].string), inline=False)

		await ctx.message.delete()
		await ctx.send(embed=embed)

		embed = discord.Embed(title="BillBoard Top 100 Lists", description="")
		
		for i in range(25, 50):
			embed.add_field(name='%3d위: ' % (i + 1),value="%s - %s" % (sp[i].string, sp1[i].string), inline=False)
			
		await ctx.send(embed=embed)
		
		embed = discord.Embed(title="BillBoard Top 100 Lists", description="")

		for i in range(50, 75):
			embed.add_field(name='%3d위: ' % (i + 1), value="%s - %s" % (sp[i].string, sp1[i].string), inline=False)
			
		await ctx.send(embed=embed)
		
		embed = discord.Embed(title="BillBoard Top 100 Lists", description="")
		for i in range(75, 100):
			embed.add_field(name='%3d위: ' % (i + 1), value="%s - %s" % (sp[i].string, sp1[i].string), inline=False)

		await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(MusicChart(bot))













