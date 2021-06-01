import asyncio, discord
import random, datetime
import requests, re
import youtube_dl, ffmpeg
import urllib
import urllib.request
import bs4
import os, sys, json
import parser
import psutil
import school_meal
from discord.ext import commands, tasks
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup #패키지 설치 필수

bot = commands.Bot(command_prefix="!")

with open("D:/token.txt", "r") as f:
    token = f.read()
    #token

with open('D:/list.json', 'r') as f:
    json_data = json.load(f)

schcode = ""
playing = {}
reaction_id = ""
cnt = 0

def weatherinfo(location):
    key = "23fb1206721ca9dd443fbc3f6b4f20ec"
    url = "http://api.openweathermap.org/data/2.5/forecast?q="+location+"&cnt=10&units=metric&lang=kr&APPID="+key

    html = requests.get(url).text
    data = json.loads(html)

    return data

def yt(name):
    with open('D:/key.json', 'r') as f:
        yt_key = json.load(f)
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'key' : yt_key['yt_key'],
        'q' : name,
        'part' : 'snippet',
        'maxResults' : 5
        }

    html = requests.get(url, params=params).json()
    items = html['items']

    result = []

    for i in items:
        title = i['snippet']['title']
        tag = i['id']['videoId']

        result1 = {
            "title" : title,
            "tag" : tag
        }
        
        result.append(result1)

    return result

def stid(name,n):
    key = "0XeO7nbthbiRoMUkYGGah20%2BfXizwc0A6BfjrkL6qhh2%2Fsl8j9PzfSLGKnqR%2F1v%2F%2B6AunxntpLfoB3Ryd3OInQ%3D%3D"
    name = urllib.parse.quote(name)
    url = "http://61.43.246.153/openapi-data/service/busanBIMS2/busStop?serviceKey="+key+"&pageNo=1&numOfRows=10&bstopnm="+name
    doc = urllib.request.urlopen(url)
    xml1 = BeautifulSoup(doc,"html.parser")
    stopid2 = xml1.findAll('bstopid',string=True)

    if n == 1:
        stopid1 = str(stopid2[0])
        stopid = stopid1[9:18]
    elif n == 2:
        stopid1 = str(stopid2[1])
        stopid = stopid1[9:18]
    return stopid

def lineid(lineno):    
    lineurl = "http://61.43.246.153/openapi-data/service/busanBIMS2/busInfo?lineno="+lineno+"&serviceKey=0XeO7nbthbiRoMUkYGGah20%2BfXizwc0A6BfjrkL6qhh2%2Fsl8j9PzfSLGKnqR%2F1v%2F%2B6AunxntpLfoB3Ryd3OInQ%3D%3D"
    lineid2 = urllib.request.urlopen(lineurl)
    lineid1 = BeautifulSoup(lineid2, "html.parser")
    lineid0 = lineid1.find('item')
    lineid = lineid0.lineid.string

    return lineid

def nextstop(no, lineno):
    lineid1 = lineid(lineno)
    url = "http://61.43.246.153/openapi-data/service/busanBIMS2/busInfoRoute?lineid="+lineid1+"&serviceKey=0XeO7nbthbiRoMUkYGGah20%2BfXizwc0A6BfjrkL6qhh2%2Fsl8j9PzfSLGKnqR%2F1v%2F%2B6AunxntpLfoB3Ryd3OInQ%3D%3D"
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
    result = {'high': {}}
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

    response = json.loads(requests.post('https://www.schoolinfo.go.kr/ei/ss/Pneiss_a01_l0.do',
                                        headers=headers, data=data).text)

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
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game("떼껄룩 바보"))

    
@bot.command()
async def 인텔(ctx):
    with open('intel-logo.jpg', 'rb') as f:
        picture = discord.File(f)
        await ctx.message.delete()
        await ctx.send(file=picture)

@bot.command()
async def 서버정보(ctx):
    embed = discord.Embed(title=ctx.guild.name+" 정보", description="")
    embed.add_field(name='서버 위치: ', value=ctx.guild.region, inline=False)
    try:
        embed.add_field(name='서버 소유자: ', value=ctx.guild.owner.nick, inline=False)
    except:
        embed.add_field(name='서버 소유자: ', value='알수 없음', inline=False)
    embed.add_field(name='인원수: ', value=ctx.guild.member_count, inline=False)
    embed.add_field(name='생성 일자: ', value=str(ctx.guild.created_at.year)+"년 "+str(ctx.guild.created_at.month)+"월 "+str(ctx.guild.created_at.day)+"일", inline=False)
    await ctx.message.delete()
    await ctx.send(embed = embed)

@bot.command()
async def 추방(ctx):
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
async def 멜론(ctx):        
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}
    melon = requests.get('https://www.melon.com/chart/index.htm', headers = header) # 멜론차트 웹사이트
    html = melon.text
    parse= BeautifulSoup(html, 'html.parser')

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
        embed.add_field(name='%3d위: '%(i+1), value="%s - %s"%(title[i], song[i]), inline=False)

    await ctx.message.delete()
    await ctx.send(embed = embed)

    embed = discord.Embed(title="멜론 실시간 차트", description="")
 
    for i in range(25, 50):
        embed.add_field(name='%3d위: '%(i+1), value="%s - %s"%(title[i], song[i]), inline=False)

    await ctx.send(embed = embed)

@bot.command()
async def 빌보드(ctx):
    url = 'https://www.billboard.com/charts/hot-100'
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')

    sp = soup.find_all('span', {'class': 'chart-element__information__song text--truncate color--primary'})
    sp1 = soup.find_all('span', {'class': 'chart-element__information__artist text--truncate color--secondary'})

    embed = discord.Embed(title="BillBoard Top 100 Lists", description="")
 
    for i in range(25):
        embed.add_field(name='%3d위: '%(i+1), value="%s - %s"%(sp[i].string, sp1[i].string), inline=False)

    await ctx.message.delete()
    await ctx.send(embed = embed)

    embed = discord.Embed(title="BillBoard Top 100 Lists", description="")
 
    for i in range(25, 50):
        embed.add_field(name='%3d위: '%(i+1), value="%s - %s"%(sp[i].string, sp1[i].string), inline=False)

    await ctx.send(embed = embed)

    embed = discord.Embed(title="BillBoard Top 100 Lists", description="")

    for i in range(50, 75):
        embed.add_field(name='%3d위: '%(i+1), value="%s - %s"%(sp[i].string, sp1[i].string), inline=False)

    await ctx.send(embed = embed)

    embed = discord.Embed(title="BillBoard Top 100 Lists", description="")
        
    for i in range(75, 100):
        embed.add_field(name='%3d위: '%(i+1), value="%s - %s"%(sp[i].string, sp1[i].string), inline=False)

    await ctx.send(embed = embed)

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
    now = datetime.datetime.now()
    embed = discord.Embed(title="현재 시각 ", description="지금 시간은")
    embed.set_footer(text = str(now.year) + "년 " + str(now.month) + "월 " + str(now.day) + "일 | " + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second))
    await ctx.message.delete()
    await ctx.send(embed=embed)

@bot.command()
async def 자기소개(ctx):
    embed=discord.Embed(title="반갑습네다 동무들", description="이곳은 신사들의 공간입네다.", color=0x620fc7)
    embed.set_author(name="Lv.99 BOSS", icon_url="https://imgur.com/vqJlpIT.png")
    embed.set_thumbnail(url="https://imgur.com/4Y0toA1.png")
    embed.set_footer(text="서버 부스터에게는 VIP 권한을 드립니다.")
    await ctx.message.delete()
    await ctx.send(embed=embed)

@bot.command()
async def connect(ctx):
        channel = ctx.author.voice.channel
        if not channel:
            await ctx.send("음성 채널에 연결후 사용해 주십시오.")
            return
        await ctx.message.delete()
        await channel.connect()

@bot.command()
async def play(ctx):
    global playing

    req = '영상 제목을 입력하십시오.'
    ans = discord.Embed(title="YouTube", description=req, color=0xcceeff)
    await ctx.send(embed=ans, delete_after=15)
    await ctx.message.delete()
    name1 = await bot.wait_for('message', timeout=15.0)
    print(name1)
    name = str(name1.content)
    await name1.delete()

    dic = yt(name)

    req = '다음중 1개를 고르시오'
    ans = discord.Embed(title="YouTube", description=req, color=0xcceeff)
    i = 1

    for data in dic:
        name = data['title']
        ans.add_field(name=i, value=name, inline=False)
        i += 1
        
    await ctx.send(embed=ans, delete_after=15)
    num1 = await bot.wait_for('message', timeout=15.0)
    num = int(num1.content)
    await num1.delete()

    url = "https://www.youtube.com/watch?v="+dic[num-1]['tag']
    print(ctx.voice_client.session_id)
    playing[ctx.guild.id] = {}
    playing[ctx.guild.id][ctx.voice_client.session_id] = dic[num-1]['title']

    song_there = os.path.isfile("song.mp3")

    try:
        if song_there:
            os.remove("song.mp3")

    except PermissionError:
        await ctx.send("오류! 재생 실패")
        return

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    print(url)

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, 'song.mp3')

    voice = bot.voice_clients
    for i in voice:
        if i.channel == ctx.author.voice.channel:
            i.play(discord.FFmpegPCMAudio("song.mp3"))
            i.volume = 100
            embed = discord.Embed(title="Now Playing", description=playing[ctx.guild.id][ctx.voice_client.session_id], color=0xcceeff)
            await ctx.send(embed=embed, delete_after=5)

@bot.command()
async def pause(ctx):
    client = ctx.voice_client
    if not client or not client.is_playing():
            return await ctx.send('Currently playing anything', delete_after=5)
    elif client.is_paused():
        return

    await ctx.message.delete()

    client.pause()
    embed = discord.Embed(title='**'+ctx.author.name+'**', description='Paused the song', color=0xcceeff)
    await ctx.send(embed=embed, delete_after=5)

@bot.command()
async def resume(ctx):
    client = ctx.voice_client
    if not client or not client.is_connected():
            return await ctx.send('Currently Not playing anything', delete_after=5)
    elif not client.is_paused():
        return

    await ctx.message.delete()

    client.resume()
    embed = discord.Embed(title='**'+ctx.author.name+'**', description='Resumed the song', color=0xcceeff)
    await ctx.send(embed=embed, delete_after=5)


@bot.command()
async def status(ctx):
    global playing

    voice = bot.voice_clients
    await ctx.message.delete()
    if not(playing[ctx.guild.id][ctx.voice_client.session_id]):
        text = "Nothing"
    else:
        text = playing[ctx.guild.id][ctx.voice_client.session_id]
    print(text)
    for i in voice:
        if i.channel == ctx.author.voice.channel:
            embed = discord.Embed(title="Now Playing", description=text, color=0xcceeff)
            await ctx.send(embed=embed, delete_after=5)

@bot.command()
async def test(ctx):
    voice = bot.voice_clients
    await ctx.message.delete()
    for i in voice:
        if i.channel == ctx.author.voice.channel:
            i.play(discord.FFmpegPCMAudio("test.flac"))
            i.is_playing()

@bot.command()
async def leave(ctx):
    global playing
    song_there = os.path.isfile("song.mp3")

    try:
        if song_there:
            os.remove("song.mp3")
                
    except PermissionError:
        print("파일 삭제 실패")

    await ctx.message.delete()

    voice = bot.voice_clients
    for i in voice:
        if i.channel == ctx.author.voice.channel:
            await i.disconnect()
            if not(playing[ctx.guild.id][ctx.voice_client.session_id]):
                pass
            else:
                playing[ctx.guild.id][ctx.voice_client.session_id] = ""

@bot.command()
async def stop(ctx):
    global playing
    song_there = os.path.isfile("song.mp3")

    try:
        if song_there:
            os.remove("song.mp3")
                
    except PermissionError:
        print("파일 삭제 실패")

    await ctx.message.delete()

    voice = bot.voice_clients
    for i in voice:
        if i.channel == ctx.author.voice.channel:
            await i.stop()
            if not(playing[ctx.guild.id][ctx.voice_client.session_id]):
                pass
            else:
                playing[ctx.guild.id][ctx.voice_client.session_id] = ""
        

@bot.command()
async def 급식(ctx):
    place = '학교명을 입력하세요'
    request_e = discord.Embed(title="Send to Me", description=place, color=0xcceeff)
    await ctx.send(embed=request_e)
    await ctx.message.delete()
    schplace1 = await bot.wait_for('message', timeout=15.0)
    schplace = str(schplace1.content) #사용 가능한 형식으로 변형
    await schplace1.delete()
    print(schplace)
    print(get_code(schplace))

    global schcode #전역 변수 설정

    schcode = get_code(schplace)

    region_code = schcode[0:3]
    school_code = schcode[3:]

    request = '날짜를 보내주세요...(20201203)'
    request_e = discord.Embed(title=schplace, description=request, color=0xcceeff)
    await ctx.send(embed=request_e)
    meal_date = await bot.wait_for('message', timeout=15.0)

    #입력이 없을 경우
    if meal_date is None:
        longtimemsg = discord.Embed(title="In 15sec", description='15초내로 입력해주세요. 다시시도 : $g', color=0xff0000)
        await ctx.send(embed=longtimemsg)
        return

    meal = school_meal.eat(meal_date, region_code, school_code)

    if len(meal) == 1:
        if meal[0] == "해당하는 데이터가 없습니다":
            embed = discord.Embed(title=schplace+" 오늘의 급식")
            embed.add_field(name='데이터가 없습니다', value=meal[0])
        else:
            embed = discord.Embed(title=schplace+" 오늘의 급식")
            embed.add_field(name='중식', value=meal[0])
    else:
        embed = discord.Embed(title=schplace+" 오늘의 급식")
        embed.add_field(name='중식', value=meal[0])
        embed.add_field(name='석식', value=meal[1])

    await ctx.send(embed=embed)
        
@bot.command()
async def 날씨(ctx):
    place = '지역을 입력하세요'
    request_e = discord.Embed(title="날씨 검색", description=place, color=0xcceeff)
    await ctx.send(embed=request_e)
    await ctx.message.delete()
    location1 = await bot.wait_for('message', timeout=15.0)
    location = str(location1.content)
    await location1.delete()
    data = weatherinfo(location)
        
    name = data['city']['name']
    weather = data['list']

    print(name)


    for i in weather:
        embed = discord.Embed(
            title=location+ ' 날씨 정보',
            description=location+ ' 날씨 정보입니다.',
            colour=discord.Colour.gold()
        )
            
        date = datetime.datetime.fromtimestamp(i['dt']).strftime('%Y-%m-%d %H:%M:%S')
        print("예보 시각: "+date)
        embed.add_field(name='예보 시각', value=date, inline=False)
        temp = i['main']['temp']
        print("기온: "+str(temp))
        embed.add_field(name='기온', value=temp, inline=False)
        feel = i['main']['feels_like']
        print("체감 기온: "+str(feel))
        embed.add_field(name='체감 기온', value=feel, inline=False)
        humidity = i['main']['humidity']
        print("습도: "+str(humidity))
        embed.add_field(name='습도', value=humidity, inline=False)
        cloud = i['weather'][0]['description']
        print("구름: "+cloud)
        embed.add_field(name='구름', value=cloud, inline=False)
        await ctx.send(embed=embed)
        print("="*20)

@bot.command()
async def 서버상태(ctx):

    embed = discord.Embed(title="현재 서버 상태")
    cpu = str(psutil.cpu_percent())
    ram = str(psutil.virtual_memory())
    print(cpu+"\n"+ram)
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
        jumsu4 = jumsu3.strip()#점수표시 (11LP등등)
        print(jumsu4)

        winlose1 = jumsu1.find("span", {"class": "WinLose"})
        winlose2 = winlose1.find("span", {"class": "wins"})
        winlose2_1 = winlose1.find("span", {"class": "losses"})
        winlose2_2 = winlose1.find("span", {"class": "winratio"})

        winlose2txt = winlose2.text
        winlose2_1txt = winlose2_1.text
        winlose2_2txt = winlose2_2.text #승,패,승률 나타냄  200W 150L Win Ratio 55% 등등

        print(winlose2txt + " " + winlose2_1txt + " " + winlose2_2txt)

    channel = ctx.channel
    embed = discord.Embed(
        title='롤'+name+' 전적',
        description=name+'님의 전적입니다.',
        colour=discord.Colour.green()
    )
    if rank4=='Unranked':
        embed.add_field(name='당신의 티어', value=rank4, inline=False)
        embed.add_field(name='-당신은 언랭-', value="언랭은 더이상의 정보가 없습니다.", inline=False)
        await ctx.send(embed=embed)
    else:
        embed.add_field(name='티어', value=rank4, inline=False)
        embed.add_field(name='LP(점수)', value=jumsu4, inline=False)
        embed.add_field(name='승,패 정보', value=winlose2txt+" "+winlose2_1txt, inline=False)
        embed.add_field(name='승률', value=winlose2_2txt, inline=False)
        await ctx.send(embed=embed)
                 
@bot.command()
async def 버스(ctx):
    place = '닉네임을 입력하세요'
    request_e = discord.Embed(title="날씨 검색", description=place, color=0xcceeff)
    await ctx.send(embed=request_e)
    name = await bot.wait_for('message', timeout=15.0)
    station = str(name.content)
    key = "0XeO7nbthbiRoMUkYGGah20%2BfXizwc0A6BfjrkL6qhh2%2Fsl8j9PzfSLGKnqR%2F1v%2F%2B6AunxntpLfoB3Ryd3OInQ%3D%3D"
    url = "http://61.43.246.153/openapi-data/service/busanBIMS2/stopArr?serviceKey="+key+"&bstopid="+stid(station, 1)
    url1 = "http://61.43.246.153/openapi-data/service/busanBIMS2/stopArr?serviceKey="+key+"&bstopid="+stid(station, 2)
    
    inf1 = urllib.request.urlopen(url)
    info1 = BeautifulSoup(inf1, "html.parser")

    embed = discord.Embed(
        title=station+ '역 버스 도착 정보 1',
        description=station,
        colour=discord.Colour.gold()
    )

    print("*"*20)
    
    for item in info1.findAll('item'):
        
        min1 = ""
        station1=""
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
        
        print("버스 번호:",lineno)
        embed.add_field(name='버스 번호', value=lineno , inline=False)
        print("도착 시간:",min1)
        embed.add_field(name='도착 예정 시간', value=min1 , inline=False)
        print("남은 정류소 수:",station1)
        embed.add_field(name='남은 정류소 수', value=station1 , inline=False)
        print("다음 정류장: ", nextstop2)
        embed.add_field(name='다음 정류장', value=nextstop2 , inline=False)
        print("*"*20)

    await ctx.send(embed=embed)

    embed = discord.Embed(
        title=station+ '역 버스 도착 정보 2',
        description=station,
        colour=discord.Colour.gold()
    )

    inf2 = urllib.request.urlopen(url1)
    info2 = BeautifulSoup(inf2, "html.parser")

    print("="*30)
    print("*"*20)

    for item in info2.findAll('item'):
        
        min1 = ""
        station1=""
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

        print("버스 번호:",lineno)
        embed.add_field(name='버스 번호', value=lineno , inline=False)
        print("도착 시간:",min1)
        embed.add_field(name='도착 예정 시간', value=min1 , inline=False)
        print("남은 정류소 수:",station1)
        embed.add_field(name='남은 정류소 수', value=station1 , inline=False)
        print("다음 정류장: ", nextstop2)
        embed.add_field(name='다음 정류장', value=nextstop2 , inline=False)
        print("*"*20)

    await ctx.send(embed=embed)    

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send("반갑습니다 "+member.guild.name+"에 오신것을 환영합니다")

@bot.event
async def on_raw_reaction_add(payload):
    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
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
