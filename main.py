import discord
import random, datetime
import requests, re
import youtube_dl, ffmpeg
import urllib
import urllib.request
import bs4
import os
import json
import psutil
import school_meal
from discord.ext import commands
from urllib.request import urlopen
from bs4 import BeautifulSoup  #패키지 설치 필수

intents = discord.Intents.default()
intents.message_content = True #requires privileged intents settings from developer portal

bot = commands.Bot(command_prefix="!", intents=intents)

token = os.environ["discord_token"]

with open('list.json', 'r') as f:
    json_data = json.load(f)

for filename in os.listdir("Cogs"): #2
    if filename.endswith(".py"): #3
        bot.load_extension(f"Cogs.{filename[:-3]}")

schcode = ""
playing = {}
reaction_id = ""
cnt = 0

def stid(name, n):
    key = os.environ['bus_key']
    name = urllib.parse.quote(name)
    url = "http://61.43.246.153/openapi-data/service/busanBIMS2/busStop?serviceKey=" + key + "&pageNo=1&numOfRows=10&bstopnm=" + name
    doc = urllib.request.urlopen(url)
    xml1 = BeautifulSoup(doc, "html.parser")
    stopid2 = xml1.findAll('bstopid', string=True)

    if n == 1:
        stopid1 = str(stopid2[0])
        stopid = stopid1[9:18]
    elif n == 2:
        stopid1 = str(stopid2[1])
        stopid = stopid1[9:18]
    return stopid


def lineid(lineno):
    key = os.environ['bus_key']
    lineurl = "http://61.43.246.153/openapi-data/service/busanBIMS2/busInfo?lineno=" + lineno + "&serviceKey="+key
    lineid2 = urllib.request.urlopen(lineurl)
    lineid1 = BeautifulSoup(lineid2, "html.parser")
    lineid0 = lineid1.find('item')
    lineid = lineid0.lineid.string

    return lineid


def nextstop(no, lineno):
    key = os.environ['bus_key']
    lineid1 = lineid(lineno)
    url = "http://61.43.246.153/openapi-data/service/busanBIMS2/busInfoRoute?lineid=" + lineid1 + "&serviceKey="+key
    text = urllib.request.urlopen(url)
    soup = BeautifulSoup(text, "html.parser")
    nextidx = 0

    for item in soup.findAll('item'):
        bstop = ""

        if item.arsno == None:

            bstop = "정보가 없습니다."
        else:
            bstop = item.arsno.string

        curidx = int(item.bstopidx.string)

        if bstop == no:
            nextidx = curidx
            nextidx = nextidx + 1

        elif curidx == nextidx:
            nextstop = item.bstopnm.string
            return nextstop


def get_code(school_name):
    """
    학교별 고유 코드 가져오기
    """
    code = ""

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }

    data = {
        'HG_CD': '',
        'SEARCH_KIND': '',
        'HG_JONGRYU_GB': '',
        'GS_HANGMOK_CD': '',
        'GS_HANGMOK_NM': '',
        'GU_GUN_CODE': '',
        'SIDO_CODE': '',
        'GUGUN_CODE': '',
        'SRC_HG_NM': school_name
    }

    response = json.loads(
        requests.post('https://www.schoolinfo.go.kr/ei/ss/Pneiss_a01_l0.do',
                      headers=headers,
                      data=data).text)

    for i in range(2, 6):
        sch = response[f'schoolList0{i}']
        if sch:
            for c in range(0, len(sch)):
                code = sch[c]['SCHUL_CODE']

    return code


@bot.event
async def on_ready():
    print("Logged in ")
    print(bot.user.name)
    print(bot.user.id)
    print("===============\n")
    for i in bot.guilds:
        print(i)
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game("Loading..."))


@bot.command()
async def 인텔(ctx):
    with open('intel-logo.jpg', 'rb') as f:
        image = discord.File(f)
        embed = discord.Embed(title="Here is your image", colour=discord.Colour.gold())
        embed.set_image(url="attachment://image.png")
        
        await ctx.send(embed=embed, file=image)

@bot.command()
async def test(ctx):
    await ctx.send("test")

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Option 1', description='Description 1', emoji='🍎'),
            discord.SelectOption(label='Option 2', description='Description 2', emoji='🍊'),
            discord.SelectOption(label='Option 3', description='Description 3', emoji='🍇'),
        ]
        super().__init__(placeholder='Choose your favorite fruit...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        print(self.values[0])
        await interaction.response.send_message(f'You selected {self.values[0]}')

class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())

@bot.command()
async def select_menu(ctx):
    view = DropdownView()
    await ctx.send('Please choose an option:', view=view)        

@bot.command()
async def 서버정보(ctx):
    """Shows Server's Info
    
    It shows
    Server owner
    Sever location
    Server member's count
    Server's date of birth
    """
    embed = discord.Embed(title=ctx.guild.name + " 정보", description="")
    try:
        embed.add_field(name='서버 소유자: ',
                        value=ctx.guild.owner.nick,
                        inline=False)
    except:
        embed.add_field(name='서버 소유자: ', value='알수 없음', inline=False)
    embed.add_field(name='인원수: ', value=ctx.guild.member_count, inline=False)
    embed.add_field(name='생성 일자: ',
                    value=str(ctx.guild.created_at.year) + "년 " +
                    str(ctx.guild.created_at.month) + "월 " +
                    str(ctx.guild.created_at.day) + "일",
                    inline=False)
    await ctx.message.delete()
    await ctx.send(embed=embed)


@bot.command()
async def 추방(ctx):
    """Kick a Member
    
    Only for Authorized Personal
    """
    if not ctx.author.permissions_in(ctx.channel).kick_members:
        ans = discord.Embed(title="Access Denied", description="You don't have permission for it.", color=0xcceeff)
        await ctx.send(embed=ans)
        return

    req = '추방 대상을 입력하십시오.'
    ans = discord.Embed(title="Password", description=req, color=0xcceeff)
    await ctx.send(embed=ans)
    name = await bot.wait_for('message', timeout=15.0)
    name = str(name.content)
    print(ctx.guild.owner.nick)
    member = ctx.guild.get_member_named(name)
    print(member.nick)
    await ctx.message.delete()
    await member.kick()

@bot.command()
async def 역할(ctx):
    global reaction_id
    channel = ctx.guild.system_channel

    try:
        message = channel.last_message
        if message.author.bot:
            await message.delete()
            print('deleted')
    except:
        print("There's no message")

    message = await channel.send("공지를 읽고 다음 이모지를 누르세요.")
    reaction_id = message.id

    await message.add_reaction(emoji="\U0001F910")
    await ctx.message.delete()


@bot.command()
async def DM(ctx):
    """Send DM to a Member"""
    req = '대상을 입력하십시오.'
    ans = discord.Embed(title="DM", description=req, color=0xcceeff)
    await ctx.send(embed=ans)
    name = await bot.wait_for('message', timeout=15.0)
    name = str(name.content)
    req = '메시지를 입력하십시오.'
    ans = discord.Embed(title="DM", description=req, color=0xcceeff)
    await ctx.send(embed=ans)
    sms = await bot.wait_for('message', timeout=15.0)
    sms = str(sms.content)
    member = ctx.guild.get_member_named(name)
    print(member.nick)
    await ctx.message.delete()
    await member.create_dm()
    await member.dm_channel.send(sms)


@bot.command()
async def 시간(ctx):
    """Shows time on a Bot Server"""
    now = datetime.datetime.now()
    embed = discord.Embed(title="현재 시각 ", description="지금 시간은")
    embed.set_footer(text=str(now.year) + "년 " + str(now.month) + "월 " +
                     str(now.day) + "일 | " + str(now.hour) + ":" +
                     str(now.minute) + ":" + str(now.second))
    await ctx.message.delete()
    await ctx.send(embed=embed)

@bot.command()
async def 급식(ctx):
    """
    입력된 날짜의 학교 급식 가져오기
    """
    place = '학교명을 입력하세요'
    request_e = discord.Embed(title="Send to Me",
                              description=place,
                              color=0xcceeff)
    await ctx.send(embed=request_e)
    await ctx.message.delete()
    schplace1 = await bot.wait_for('message', timeout=15.0)
    schplace = str(schplace1.content)  #사용 가능한 형식으로 변형
    await schplace1.delete()
    print(schplace)
    print(get_code(schplace))

    global schcode  #전역 변수 설정

    schcode = get_code(schplace)

    region_code = schcode[0:3]
    school_code = schcode[3:]

    request = '날짜를 보내주세요...(20201203)'
    request_e = discord.Embed(title=schplace,
                              description=request,
                              color=0xcceeff)
    await ctx.send(embed=request_e)
    meal_date = await bot.wait_for('message', timeout=15.0)

    #입력이 없을 경우
    if meal_date is None:
        longtimemsg = discord.Embed(title="In 15sec",
                                    description='15초내로 입력해주세요. 다시시도 : $g',
                                    color=0xff0000)
        await ctx.send(embed=longtimemsg)
        return

    meal = school_meal.eat(meal_date, region_code, school_code)

    if len(meal) == 1:
        if meal[0] == "해당하는 데이터가 없습니다":
            embed = discord.Embed(title=schplace + " 오늘의 급식")
            embed.add_field(name='데이터가 없습니다', value=meal[0])
        else:
            embed = discord.Embed(title=schplace + " 오늘의 급식")
            embed.add_field(name='중식', value=meal[0])
    else:
        embed = discord.Embed(title=schplace + " 오늘의 급식")
        embed.add_field(name='중식', value=meal[0])
        embed.add_field(name='석식', value=meal[1])

    await ctx.send(embed=embed)

@bot.command()
async def 서버상태(ctx):
    """Show server's status
    
    It shows
    Server's CPU Usage
    Server's RAM Usage
    """

    embed = discord.Embed(title="현재 서버 상태")
    cpu = str(psutil.cpu_percent())
    ram = str(psutil.virtual_memory())
    print(cpu + "\n" + ram)
    embed.add_field(name="CPU Usage: ", value=cpu, inline=False)
    embed.add_field(name="RAM Usage: ", value=ram, inline=False)
    await ctx.message.delete()
    await ctx.send(embed=embed)


@bot.command()
async def 롤(ctx):
    place = '닉네임을 입력하세요'
    request_e = discord.Embed(title="날씨 검색", description=place, color=0xcceeff)
    await ctx.send(embed=request_e)
    name = await bot.wait_for('message', timeout=15.0)
    name = str(name.content)
    enc_name = urllib.parse.quote(name)

    url = "http://www.op.gg/summoner/userName=" + enc_name
    html = urllib.request.urlopen(url)

    bsObj = bs4.BeautifulSoup(html, "html.parser")
    rank1 = bsObj.find("div", {"class": "TierRankInfo"})
    rank2 = rank1.find("div", {"class": "TierRank"})
    rank4 = rank2.text  # 티어표시 (브론즈1,2,3,4,5 등등)
    print(rank4)
    if rank4 != 'Unranked':
        jumsu1 = rank1.find("div", {"class": "TierInfo"})
        jumsu2 = jumsu1.find("span", {"class": "LeaguePoints"})
        jumsu3 = jumsu2.text
        jumsu4 = jumsu3.strip()  #점수표시 (11LP등등)
        print(jumsu4)

        winlose1 = jumsu1.find("span", {"class": "WinLose"})
        winlose2 = winlose1.find("span", {"class": "wins"})
        winlose2_1 = winlose1.find("span", {"class": "losses"})
        winlose2_2 = winlose1.find("span", {"class": "winratio"})

        winlose2txt = winlose2.text
        winlose2_1txt = winlose2_1.text
        winlose2_2txt = winlose2_2.text  #승,패,승률 나타냄  200W 150L Win Ratio 55% 등등

        print(winlose2txt + " " + winlose2_1txt + " " + winlose2_2txt)

    channel = ctx.channel
    embed = discord.Embed(title='롤' + name + ' 전적',
                          description=name + '님의 전적입니다.',
                          colour=discord.Colour.green())
    if rank4 == 'Unranked':
        embed.add_field(name='당신의 티어', value=rank4, inline=False)
        embed.add_field(name='-당신은 언랭-',
                        value="언랭은 더이상의 정보가 없습니다.",
                        inline=False)
        await ctx.send(embed=embed)
    else:
        embed.add_field(name='티어', value=rank4, inline=False)
        embed.add_field(name='LP(점수)', value=jumsu4, inline=False)
        embed.add_field(name='승,패 정보',
                        value=winlose2txt + " " + winlose2_1txt,
                        inline=False)
        embed.add_field(name='승률', value=winlose2_2txt, inline=False)
        await ctx.send(embed=embed)


@bot.command()
async def 버스(ctx):
    place = '닉네임을 입력하세요'
    request_e = discord.Embed(title="날씨 검색", description=place, color=0xcceeff)
    await ctx.send(embed=request_e)
    name = await bot.wait_for('message', timeout=15.0)
    station = str(name.content)
    key = os.environ['bus_key']
    url = "http://61.43.246.153/openapi-data/service/busanBIMS2/stopArr?serviceKey=" + key + "&bstopid=" + stid(
        station, 1)
    url1 = "http://61.43.246.153/openapi-data/service/busanBIMS2/stopArr?serviceKey=" + key + "&bstopid=" + stid(
        station, 2)

    inf1 = urllib.request.urlopen(url)
    info1 = BeautifulSoup(inf1, "html.parser")

    embed = discord.Embed(title=station + '역 버스 도착 정보 1',
                          description=station,
                          colour=discord.Colour.gold())

    print("*" * 20)

    for item in info1.findAll('item'):

        min1 = ""
        station1 = ""
        nextstop2 = ""
        no = ""

        if item.arsno == None:
            no = "정보가 없습니다."
        else:
            no = item.arsno.string

        lineno = item.lineno.string
        nextstop1 = nextstop(no, lineno)

        if item.min1 == None:
            min1 = "정보가 없습니다."
        else:
            min1 = item.min1.string

        if item.station1 == None:

            station1 = "정보가 없습니다."
        else:
            station1 = item.station1.string

        if nextstop1 == None:

            nextstop2 = "정보가 없습니다."

        else:
            nextstop2 = nextstop1

        print("버스 번호:", lineno)
        embed.add_field(name='버스 번호', value=lineno, inline=False)
        print("도착 시간:", min1)
        embed.add_field(name='도착 예정 시간', value=min1, inline=False)
        print("남은 정류소 수:", station1)
        embed.add_field(name='남은 정류소 수', value=station1, inline=False)
        print("다음 정류장: ", nextstop2)
        embed.add_field(name='다음 정류장', value=nextstop2, inline=False)
        print("*" * 20)

    await ctx.send(embed=embed)

    embed = discord.Embed(title=station + '역 버스 도착 정보 2',
                          description=station,
                          colour=discord.Colour.gold())

    inf2 = urllib.request.urlopen(url1)
    info2 = BeautifulSoup(inf2, "html.parser")

    print("=" * 30)
    print("*" * 20)

    for item in info2.findAll('item'):

        min1 = ""
        station1 = ""
        nextstop2 = ""
        no = ""

        if item.arsno == None:
            no = "정보가 없습니다."
        else:
            no = item.arsno.string

        lineno = item.lineno.string
        nextstop1 = nextstop(no, lineno)

        if item.min1 == None:
            min1 = "정보가 없습니다."
        else:
            min1 = item.min1.string

        if item.station1 == None:

            station1 = "정보가 없습니다."
        else:
            station1 = item.station1.string

        if nextstop1 == None:

            nextstop2 = "정보가 없습니다."

        else:
            nextstop2 = nextstop1

        print("버스 번호:", lineno)
        embed.add_field(name='버스 번호', value=lineno, inline=False)
        print("도착 시간:", min1)
        embed.add_field(name='도착 예정 시간', value=min1, inline=False)
        print("남은 정류소 수:", station1)
        embed.add_field(name='남은 정류소 수', value=station1, inline=False)
        print("다음 정류장: ", nextstop2)
        embed.add_field(name='다음 정류장', value=nextstop2, inline=False)
        print("*" * 20)

    await ctx.send(embed=embed)

@bot.command()
async def load(ctx, extension):
    """Command which Loads a Module."""

    if not (await bot.is_owner(ctx.author)):
        ans = discord.Embed(title="Access Denied", description="You don't have permission for it.", color=0xcceeff)
        await ctx.send(embed=ans)
        return

    try:
        print("loading "+extension)
        await bot.load_extension("Cogs."+extension)
    except Exception as e:
        await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
        await ctx.send('**`SUCCESS`**')

@bot.command()
async def unload(ctx, extension):
    """Command which Unloads a Module."""

    if not bot.is_owner(ctx.author):
        ans = discord.Embed(title="Access Denied", description="You don't have permission for it.", color=0xcceeff)
        await ctx.send(embed=ans)
        return

    try:
        await bot.unload_extension("Cogs."+extension)
    except Exception as e:
        await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
        await ctx.send('**`SUCCESS`**')

@bot.command()
async def reload(ctx, extension):
    """Command which Reloads a Module."""

    if not bot.is_owner(ctx.author):
        ans = discord.Embed(title="Access Denied", description="You don't have permission for it.", color=0xcceeff)
        await ctx.send(embed=ans)
        return

    try:
        await bot.reload_extension("Cogs."+extension)
    except Exception as e:
        await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
        await ctx.send('**`SUCCESS`**')

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send("반갑습니다 " + member.guild.name + "에 오신것을 환영합니다")

@bot.event
async def on_raw_reaction_add(payload):
    message = await bot.get_channel(payload.channel_id
                                    ).fetch_message(payload.message_id)
    user = payload.member
    print(payload.emoji)
    print(message.channel.id)
    print(user)

    if (message.channel.id == user.guild.system_channel.id):
        if (payload.emoji == "\U0001F910"):
            print('mafia')
        if str(user.guild.id) in json_data:
            global cnt
            if (not user.bot) and (cnt == 0):
                role_id = json_data[str(user.guild.id)]
                role = user.guild.get_role(int(role_id))
                print(role_id)
                await user.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
    channel = await bot.fetch_channel(payload.channel_id)
    guild = channel.guild

    user = await guild.fetch_member(payload.user_id)
    print(channel.id)
    message = await channel.fetch_message(payload.message_id)
    print(payload.emoji)
    print(guild.system_channel)

    if (channel.id == guild.system_channel.id):
        if str(guild.id) in json_data:
            role_id = json_data[str(guild.id)]
            role = guild.get_role(int(role_id))
            print(role)
            await user.remove_roles(role)


bot.run(token)
