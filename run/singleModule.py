# -*- coding:utf-8 -*-
import asyncio
import datetime
import json
import os
import random
import re
import urllib
from asyncio import sleep
from io import BytesIO
from pathlib import Path

import httpx
import yaml
from plugins.historicalToday import hisToday as hisToday1
from plugins import weatherQuery
from plugins.RandomStr import random_str
from plugins.arkOperator import arkOperator
from plugins.cpGenerate import get_cp_mesg
from plugins.gacha import arkGacha, starRailGacha
from plugins.genshinGo import genshinDraw, qianCao
from plugins.jokeMaker import get_joke
from plugins.newLogger import newLogger
from plugins.newsEveryDay import news, moyu, xingzuo, sd
from plugins.picGet import pic, setuGet, picDwn
from plugins.tarot import tarotChoice
from PIL import Image as Image1

from nonebot import on_command, on_fullmatch, on_startswith, on_keyword, on_regex, on_endswith
from nonebot.adapters.red import Bot
from nonebot.adapters.red.event import MessageEvent
from nonebot.adapters.red.message import MessageSegment, Message
from nonebot.rule import to_me, startswith
#指令部分
from plugins.translater import translate
from plugins.webScreenShoot import screenshot_to_pdf_and_png

getMeme=on_fullmatch("meme")
yunshi=on_fullmatch("运势")
TodatTarot=on_fullmatch("今日塔罗")
colorAnime=on_fullmatch("彩色小人")
picGetter=on_endswith("图")
picGetter2= on_startswith("/")#on_regex(r'(\d+)张(\w+)',flags=re.IGNORECASE)
hisToday=on_startswith("历史上的")
weatherQuery9=on_startswith("查询")
newss=on_fullmatch("新闻")
moyurenlili=on_fullmatch("摸鱼")
xingzuoQuery=on_fullmatch("星座")
jokes=on_endswith("笑话")
cpGene=on_startswith("/cp")
nasa_every=on_fullmatch("天文")
operator=on_fullmatch("干员生成")
opStart=on_fullmatch("原神启动")
qiancao=on_fullmatch("抽签")
poetrys=on_fullmatch("诗经")
YiChou=on_fullmatch("周易")
screenShoot1=on_startswith("截图#")
honorYou=on_startswith("/奖状")
ark10=on_fullmatch("方舟十连")
starRailOrdor=on_fullmatch("星铁十连")
#拿数据
logger=newLogger()

with open('config/api.yaml', 'r', encoding='utf-8') as f:
    result121 = yaml.load(f.read(), Loader=yaml.FullLoader)
api_KEY=result121.get("weatherXinZhi")
app_id=result121.get("youdao").get("app_id")
app_key=result121.get("youdao").get("app_key")
nasa_api=result121.get("nasa_api")

proxy=result121.get("proxy")
logger.info("抽卡/运势模块启动")
logger.info("额外的功能 启动完成")
with open("data/odes.json", encoding="utf-8") as fp:
    odes = json.loads(fp.read())
with open("data/IChing.json", encoding="utf-8") as fp:
    IChing = json.loads(fp.read())
global data
with open('data/nasaTasks.yaml', 'r', encoding='utf-8') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)
with open('data/userData.yaml', 'r', encoding='utf-8') as file:
    data1 = yaml.load(file, Loader=yaml.FullLoader)
global trustUser
userdict = data1
trustUser = []
for i in userdict.keys():
    data2 = userdict.get(i)
    times = int(str(data2.get('sts')))
    if times > 8:
        trustUser.append(str(i))
with open('config/settings.yaml', 'r', encoding='utf-8') as f:
    result1 = yaml.load(f.read(), Loader=yaml.FullLoader)
r18 = result1.get("r18Pic")
global picData
picData = {}
colorfulCharacterList = os.listdir("data/colorfulAnimeCharacter")


@getMeme.handle()
async def meme(bot: Bot, event: MessageEvent):
    global memeData

    try:
        logger.info("使用网络meme")

        url = 'https://meme-api.com/gimme'
        proxies = {
            "http://": proxy,
            "https://": proxy
        }
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url)
            logger.info(r.json().get("preview")[-1])
            async with httpx.AsyncClient(timeout=20, proxies=proxies) as client:
                r = await client.get(r.json().get("preview")[-1])
                img = Image1.open(BytesIO(r.content))  # 从二进制数据创建图片对象
                path = "data/pictures/meme/" + random_str() + ".png"
                img.save(path)  # 使用PIL库保存图片
                await bot.send_group_message(event.scene, MessageSegment.image(Path(path)))


    except:
        logger.warning("网络meme出错，使用本地meme图")
        la = os.listdir("data/pictures/meme")
        la = "data/pictures/meme/" + random.choice(la)
        logger.info("掉落了一张meme图")
        await bot.send_group_message(event.scene, MessageSegment.image(Path(la)))

@yunshi.handle()
async def meme(bot: Bot, event: MessageEvent):
    global memeData

    la = os.listdir("data/pictures/amm")
    la = "data/pictures/amm/" + random.choice(la)
    logger.info("执行运势查询")
    await bot.send_group_message(event.scene, (event.sendMemberName+"今天的运势是",MessageSegment.image(Path(la))))

@TodatTarot.handle()
async def tarotToday(bot: Bot, event: MessageEvent):
    logger.info("获取今日塔罗")
    txt, img = tarotChoice()
    logger.info("成功获取到今日塔罗")
    await bot.send_group_message(event.scene, (txt,MessageSegment.image(Path(img))))

@colorAnime.handle()
async def tarotToday(bot: Bot, event: MessageEvent):
        logger.info("彩色小人，启动！")
        c = random.choice(colorfulCharacterList)
        await bot.send_group_message(event.scene, MessageSegment.image(Path("data/colorfulAnimeCharacter/" + c)))

@picGetter.handle()
async def handle_group_message(bot: Bot, event: MessageEvent):
    # if str(event.get_plaintext()) == '/pic':

    if get_number(str(event.get_plaintext())) == None:
        return
    else:
        picNum = int(get_number(str(event.get_plaintext())))
        logger.info("图片获取指令....数量：" + str(picNum))
        if picNum < 10 and picNum > -1:
            for i in range(picNum):
                logger.info("获取壁纸")
                a = pic()
                await bot.send_group_message(event.scene, MessageSegment.image(Path(a)))
        elif picNum == '':
            a = pic()
            await bot.send_group_message(event.scene, MessageSegment.image(Path(a)))
        else:
            await bot.send(event, "数字超出限制")
        logger.info("图片获取完成")


# 整点正则
pattern = r".*(壁纸|图|pic).*(\d+).*|.*(\d+).*(壁纸|图|pic).*"


# 定义一个函数，使用正则表达式检查字符串是否符合条件，并提取数字
def get_number(string):
    # 使用re.match方法，返回匹配的结果对象
    # 使用re.match方法，返回匹配的结果对象
    match = re.match(pattern, string)
    # 如果结果对象不为空，返回捕获的数字，否则返回None
    if match:
        # 如果第二个分组有值，返回第二个分组，否则返回第三个分组
        if match.group(2):
            return match.group(2)
        else:
            return match.group(3)
    else:
        return None


@picGetter2.handle()
async def setuHelper(bot: Bot, event: MessageEvent):
    pattern1 = r'(\d+)张(\w+)'
    global picData

    text1 = str(event.get_plaintext()).replace("壁纸", "").replace("涩图", "").replace("色图", "").replace("图", "").replace(
        "r18", "")
    match1 = re.search(pattern1, text1)
    if match1:
        logger.info("提取图片关键字。 数量: " + str(match1.group(1)) + " 关键字: " + match1.group(2))
        data = {"tag": ""}
        if "r18" in str(event.get_plaintext()) or "色图" in str(event.get_plaintext()) or "涩图" in str(
                event.get_plaintext()):
            if str(event.senderUin) in trustUser and r18 == True:
                data["r18"] = 1
            else:
                await bot.send(event, "r18模式已关闭")
        picData[event.senderUin] = []
        data["tag"] = match1.group(2)
        data["size"] = "regular"
        logger.info("组装数据完成：" + str(data))
        a = int(match1.group(1))
        if int(match1.group(1)) > 6:
            a = 5
            await bot.send(event, "api访问限制，修改获取张数为 5")
        for i in range(a):
            try:
                path = await setuGet(data)
            except:
                logger.error("涩图请求出错")
                await bot.send(event, "请求出错，请稍后再试")
                return
            logger.info("发送图片: " + path)
            try:
                await bot.send_group_message(event.scene, MessageSegment.image(Path(path)))
                logger.info("图片发送成功")
            except:
                logger.error("图片发送失败")
                await bot.send(event, path)
            '''try:
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain([" " , Image(url=path)]))
                picData.get(event.senderUin).append(b1)
            except:
                logger.error("出错，转为url文本")
                b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                        message_chain=MessageChain([" " , path]))
                picData.get(event.senderUin).append(b1)

        await bot.send(event, Forward(node_list=picData.get(event.senderUin)))
        picData.pop(event.senderUin)'''


@hisToday.handle()
async def historyToday(bot: Bot, event: MessageEvent):
    pattern = r".*史.*今.*|.*今.*史.*"
    string = str(event.get_plaintext())
    match = re.search(pattern, string)
    if match:
        dataBack = await hisToday1()
        logger.info("获取历史上的今天")
        logger.info(str(dataBack))
        sendData = str(dataBack.get("result")).replace("[", " ").replace("{'year': '", "").replace("'}", "").replace(
            "]", "").replace("', 'title': '", " ").replace(",", "\n")
        await bot.send(event, sendData)


@weatherQuery9.handle()
async def weather_query(bot: Bot, event: MessageEvent):
    # 从消息链中取出文本

    # 匹配指令
    m = re.match(r'^查询\s*(\w+)\s*$', event.get_plaintext())
    if m:
        # 取出指令中的地名
        city = m.group(1)
        logger.info("查询 " + city + " 天气")
        await bot.send(event, '查询中……')
        # 发送天气消息
        await bot.send(event, await weatherQuery.querys(city, api_KEY))


@newss.handle()
async def newsToday(bot: Bot, event: MessageEvent):

    logger.info("获取新闻")
    path = await news()
    logger.info("成功获取到今日新闻")
    await bot.send_group_message(event.scene, MessageSegment.image(Path(path)))


@moyurenlili.handle()
async def moyuToday(bot: Bot, event: MessageEvent):

    logger.info("获取摸鱼人日历")
    path = await moyu()
    logger.info("成功获取到摸鱼人日历")
    await bot.send_group_message(event.scene, MessageSegment.image(Path(path)))


@xingzuoQuery.handle()
async def moyuToday(bot: Bot, event: MessageEvent):
    logger.info("获取星座运势")
    path = await xingzuo()
    logger.info("成功获取到星座运势")
    await bot.send_group_message(event.scene, MessageSegment.image(Path(path)))



@jokes.handle()
async def make_jokes(bot: Bot, event: MessageEvent):

    x = str(event.get_plaintext()).strip()[0:-2]
    joke = get_joke(x)
    await bot.send(event, joke)


# 凑个cp
@cpGene.handle()
async def make_cp_mesg(bot: Bot, event: MessageEvent):
    x = str(event.get_plaintext()).replace('/cp ', '', 1)
    x = x.split(' ')
    if len(x) != 2:
        path = '../data/voices/' + random_str() + '.wav'
        text = 'エラーが発生しました。再入力してください'
        try:
            tex = '[JA]' + text + '[JA]'
            logger.info("启动文本转语音：text: " + tex + " path: " + path[3:])
            await voiceGenerate({"text": tex, "out": path})
            await bot.send(event, Voice(path=path))
        except:
            await bot.send(event,text)
        return
    mesg = get_cp_mesg(x[0], x[1])
    await bot.send(event, mesg, True)


@nasa_every.handle()
async def NasaHelper(bot: Bot, event: MessageEvent):
    global data

    logger.info(str(data.keys()))
    if datetime.datetime.now().strftime('%Y-%m-%d') in data.keys():
        todayNasa = data.get(datetime.datetime.now().strftime('%Y-%m-%d'))
        path = todayNasa.get("path")
        txt = todayNasa.get("transTxt")
        try:
            await bot.send_group_message(event.scene, MessageSegment.image(Path(path)))
            await bot.send(event,txt)
            #await bot.send(event, (Image(path=path), txt))
        except:
            await bot.send(event, txt)
    else:
        proxies = {
            "http://": proxy,
            "https://": proxy
        }
        # Replace the key with your own
        dataa = {"api_key": nasa_api}
        logger.info("发起nasa请求")
        try:
            # 拼接url和参数
            url = "https://api.nasa.gov/planetary/apod?" + "&".join([f"{k}={v}" for k, v in dataa.items()])
            async with httpx.AsyncClient(proxies=proxies) as client:
                # 用get方法发送请求
                response = await client.get(url=url)
            # response = requests.post(url="https://saucenao.com/search.php", data=dataa, proxies=proxies)
            logger.info("获取到结果" + str(response.json()))
            # logger.info("下载缩略图")
            filename = await picDwn(response.json().get("url"),
                                    "data/pictures/nasa/" + response.json().get("date") + ".png")
            txta = await translate(response.json().get("explanation"), app_id=app_id, app_key=app_key, ori="en",
                                   aim="zh-CHS")
            txt = response.json().get("date") + "\n" + response.json().get("title") + "\n" + txta
            temp = {"path": "data/pictures/nasa/" + response.json().get("date") + ".png",
                    "oriTxt": response.json().get("explanation"), "transTxt": txt}

            data[datetime.datetime.now().strftime('%Y-%m-%d')] = temp

            with open('data/nasaTasks.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(data, file, allow_unicode=True)
            await bot.send_group_message(event.scene, (txt,MessageSegment.image(Path(filename))))

            #await bot.send(event, (Image(path=filename), txt))

        except:
            logger.warning("获取每日天文图片失败")
            await bot.send(event, "获取失败，请联系master检查代理或api_key是否可用")


@operator.handle()
async def arkGene(bot: Bot, event: MessageEvent):
        logger.info("又有皱皮了，生成干员信息中.....")
        o = arkOperator()
        o = o.replace("为生成", event.sendMemberName)
        await bot.send(event, o)


@opStart.handle()
async def genshin1(bot: Bot, event: MessageEvent):

    logger.info("有原皮！获取抽签信息中....")
    o = genshinDraw()
    logger.info("\n" + o)
    await bot.send(event, o)


@qiancao.handle()
async def genshin1(bot: Bot, event: MessageEvent):
    logger.info("获取浅草百签")
    o = qianCao()
    logger.info(o)
    await bot.send(event, o)


@poetrys.handle()
async def NasaHelper(bot: Bot, event: MessageEvent):

    logger.info("获取一篇诗经")
    ode = random.choice(odes.get("诗经"))
    logger.info("\n" + ode)
    await bot.send(event, ode)


@YiChou.handle()
async def NasaHelper(bot: Bot, event: MessageEvent):

    logger.info("获取卦象")
    IChing1 = random.choice(IChing.get("六十四卦"))
    logger.info("\n" + IChing1)
    await bot.send(event, IChing1)


@screenShoot1.handle()
async def screenShoot(bot: Bot, event: MessageEvent):
    url=str(event.get_plaintext()).replace("截图#","")
    path = "data/pictures/cache/" + random_str() + ".png"
    logger.info("接收网页截图任务url:" + url)
    try:
        await screenshot_to_pdf_and_png(url, path)
    except:
        logger.error("截图失败!")
    await bot.send_group_message(event.scene, MessageSegment.image(Path(path)))


'''@bot.on(GroupMessage)
async def NasaHelper(bot: Bot, event: MessageEvent):
    if str(event.get_plaintext()).startswith("/sd"):
        try:

            ls = str(event.get_plaintext())[3:]
        except:
            await bot.send("未传递合法的prompt")
            return
        logger.info("拆分获取prompt:" + str(ls))
        try:
            url = "https://api.pearktrue.cn/api/stablediffusion/?prompt=" + str(ls) + "&model=normal"
            url = requests.get(url).json().get("imgurl")
        except:
            logger.error("出错")
            await bot.send(event, "出错，请稍后再试")
            return
        path = "data/pictures/cache/" + random_str() + ".png"
        try:
            p = await sd(url, path)
        except:
            logger.error("出错")
            await bot.send(event, "出错，请稍后再试")
            return
        await bot.send(event, Image(path=p), True)'''


@honorYou.handle()
async def jiangzhuang(bot: Bot, event: MessageEvent):

    try:
        t = str(event.get_plaintext()).replace("/奖状","").split("#")
        url = "https://api.pearktrue.cn/api/certcommend/?name=" + t[0] + "&title=" + t[1] + "&classname=" + t[2]

        p = await sd(url, "data/pictures/cache/" + random_str() + ".png")
        await bot.send_group_message(event.scene, MessageSegment.image(Path(p)))
    except:
        await bot.send(event, "出错，格式请按照/奖状 孙笑川#天皇#阳光小学一年级2班")


@ark10.handle()
async def moyuToday(bot: Bot, event: MessageEvent):

    logger.info("获取方舟抽卡结果")
    try:
        path = await arkGacha()
        logger.info("成功获取到抽卡结果")
        await bot.send_group_message(event.scene, MessageSegment.image(Path(path)))
    except:
        logger.error("皱皮衮")
        await bot.send(event, "获取抽卡结果失败，请稍后再试")


@starRailOrdor.handle()
async def moyuToday(bot: Bot, event: MessageEvent):

    logger.info("获取星铁抽卡结果")
    try:
        path = await starRailGacha()
        logger.info("成功获取到星铁抽卡结果")
        await bot.send_group_message(event.scene, MessageSegment.image(Path(path)))
    except:
        logger.error("穹批衮")
        await bot.send(event, "获取抽卡结果失败，请稍后再试")

