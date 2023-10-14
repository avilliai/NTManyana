# -*- coding: utf-8 -*-
import json
import os
import datetime
import random
import time
import sys
from pathlib import Path

import yaml
from PIL import ImageFont
from PIL import ImageDraw
from PIL import Image
from plugins.RandomStr import random_str
from plugins.imgDownload import dict_download_img
from plugins.newLogger import newLogger
from plugins.weatherQuery import querys

from nonebot import on_command, on_fullmatch, on_startswith, on_keyword, on_regex, on_endswith
from nonebot.adapters.red import Bot
from nonebot.adapters.red.event import MessageEvent
from nonebot.adapters.red.message import MessageSegment, Message
from nonebot.rule import to_me, startswith
#指令区
sign=on_fullmatch("签到")
sign2=on_startswith("")
permit=on_startswith("授权#")
changeCity1=on_startswith("修改城市#")




#取数据
with open('config/api.yaml', 'r', encoding='utf-8') as f:
    result121 = yaml.load(f.read(), Loader=yaml.FullLoader)
api_KEY = result121.get("weatherXinZhi")
logger=newLogger()
with open('config/settings.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
master=result.get("master")
mainGroup = int(result.get("mainGroup"))
signMode=result.get("signMode")
logger.info("签到部分启动完成")
with open('data/userData.yaml', 'r', encoding='utf-8') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)

global userdict
userdict = data
logger.info("读取用户数据完成")
global newUser
newUser={}

@sign.handle()
async def handle_group_message(bot: Bot, event: MessageEvent):
    try:
        logger.info("接收来自："+event.sendMemberName+"("+str(int(event.senderUin))+") 的签到指令")
    except:
        logger.error("别看我，我也不知道")
    if str(int(event.senderUin)) in userdict.keys():
        data=userdict.get(str(int(event.senderUin)))
        signOrNot = data.get('ok')
        time114514 = str(datetime.datetime.now().strftime('%Y-%m-%d'))
        if signOrNot!=time114514:
            city = data.get('city')
            startTime = data.get('st')
            times = str(int(data.get('sts')) + 1)
            if times=='14':
                await bot.send(event,'词库自动授权完成,发送 开始添加 试试吧')
            exp = str(int(data.get('exp')) + random.randint(1, 20))
            nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            id = data.get('id')
            data['sts'] = times
            data['exp'] = exp
            data['ok'] = time114514
            userdict[str(int(event.senderUin))] = data
            logger.info("启动天气查询")
            weather = await querys(city,api_KEY)
            logger.info(weather)
            logger.info("更新用户数据中")
            with open('data/userData.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(userdict, file, allow_unicode=True)
            imgurl = get_user_image_url(int(event.senderUin))
            logger.info("制作签到图片....")
            path = await signPicMaker(imgurl, id, weather, nowTime, times, exp, startTime)
            logger.info("完成，发送签到图片")
            await bot.send_group_message(event.scene, MessageSegment.image(Path(path)))
        else:
            logger.info("签到过了，拒绝签到")
            await bot.send(event,'不要重复签到！笨蛋！')
    else:
        logger.info("未注册用户"+str(int(event.senderUin))+"，提醒注册")
        await bot.send(event,'请完善用户信息\n发送 注册#城市名 以完善信息\n例如 注册#通辽')
        global newUser
        newUser[str(int(event.senderUin))]=0

@sign2.handle()
async def handle_group_message(bot: Bot, event: MessageEvent):
    global newUser
    try:
        if str(int(event.senderUin)) in newUser.keys():
            newUser.pop(str(int(event.senderUin)))
            logger.info("用户+1："+str(event.sendMemberName)+" ("+str(int(event.senderUin))+")")
            time114514 = str(datetime.datetime.now().strftime('%Y-%m-%d'))
            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                city = str(event.get_plaintext()).split('#')[1]

                await bot.send(event, '正在验证城市......，')
                weather = await querys(city,api_KEY)
                await bot.send(event, '成功')
                logger.info("验证城市通过")
            except:
                await bot.send(event,'error，默认执行 注册#通辽 ,随后可发送 修改城市#城市名 进行地区修改')
                city='通辽'
                weather = await querys(city,api_KEY)
                logger.info("城市验证未通过，送进通辽当可汗子民")
            global userdict
            userdict[str(int(event.senderUin))] = {"city": city, "st": time, "sts": "1", "exp": "0",
                                              "id": random_str(6,'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'),'ok':time114514}
            data = userdict.get(str(int(event.senderUin)))
            city = data.get('city')
            startTime = data.get('st')
            times = str(int(data.get('sts')) + 1)
            exp = str(int(data.get('exp')) + random.randint(1, 20))
            nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            id = data.get('id')
            data['sts'] = times
            data['exp'] = exp
            data['userName']=event.sendMemberName
            userdict[str(int(event.senderUin))] = data
            logger.info("更新用户数据中")
            with open('data/userData.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(userdict, file, allow_unicode=True)

            imgurl = get_user_image_url(int(event.senderUin))
            logger.info("制作签到图片....")
            path=await signPicMaker(imgurl,id,weather,nowTime,times,exp,startTime)
            logger.info("完成，发送签到图片")
            await bot.send_group_message(event.scene, MessageSegment.image(Path(path)))
    except:
        pass


@permit.handle()
async def accessGiver(bot: Bot, event: MessageEvent):
    global userdict
    if int(event.peerUin)==mainGroup or int(event.senderUin)==master:
        try:
            if int(event.senderUin)==master:
                setN="99"
            else:
                setN="15"

        except:
            return

        userId=str(event.get_plaintext()).split("#")[1]
        if userId in userdict:
            data=userdict.get(userId)
            data["sts"]=setN
            userdict[userId]=data
        else:
            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            userdict[userId] = {"city": "通辽", "st": time, "sts": setN, "exp": "0",
                                              "id": "miav-"+random_str(), 'ok': time}
        logger.info("更新用户数据中")
        with open('data/userData.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(userdict, file, allow_unicode=True)
        logger.info("授权"+userId+"完成")
        await bot.send(event,"授权完成,一分钟后数据将完成同步")
        await bot.send_friend_message(int(userId),"授权完成，解锁部分bot权限(一分钟后)")

@changeCity1.handle()
async def changeCity(bot: Bot, event: MessageEvent):

    logger.info("接收城市修改请求")
    city=str(event.get_plaintext()).replace("修改城市#","")
    try:

        data=userdict.get(str(int(event.senderUin)))
        await bot.send(event, '正在验证城市......，')
        weather = await querys(city,api_KEY)
        if "抱歉" in weather:
            await bot.send(event,"城市不可用，请发送 修改城市#城市名")
            return
        data['city']=city
        data["id"]=random_str(6,'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789')
        await bot.send(event, '成功')
        userdict[str(int(event.senderUin))] = data
        with open('data/userData.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(userdict, file, allow_unicode=True)
    except:
        await bot.send(event,'没有对应的城市数据......，')
async def userAvatarDownLoad(url):
    fileName = dict_download_img(url,dirc="data/pictures/avatars")
    logger.info("头像路径："+fileName)
    touxiang = Image.open(fileName)
    fad = touxiang.resize((450, 450), Image.BICUBIC)
    fad.save(fileName)
    return fileName
async def signPicMaker(url,id,weather,nowTime,times,exp,startTime):
    fileName=await userAvatarDownLoad(url)
    # 制底图
    layer = Image.open(fileName)
    if signMode==0:
        path="data/pictures/sign_backGround/ba/"+random.choice(os.listdir("data/pictures/sign_backGround"))
        bg = Image.open(path)
        # merge = Image.blend(st, st2, 0.5)
        bg.paste(layer, (120, 147))
        fileName='data/pictures/cache/'+random_str()+".png"
        bg.save(fileName)
        imageFile = fileName
        # 导入数据
        tp = Image.open(imageFile)
        font = ImageFont.truetype('data/fonts/H-TTF-BuMing-B-2.ttf', 110)
        draw = ImageDraw.Draw(tp)
        font = ImageFont.truetype('data/fonts/Caerulaarbor.ttf', 115)
        draw.text((423, 743), id, (12, 0, 6), font=font)
        font = ImageFont.truetype('data/fonts/H-TTF-BuMing-B-2.ttf', 73)
        draw.text((2000, 716), weather, (12, 0, 6), font=font)
        draw.text((509, 1419), '当前exp:' + exp, (12, 0, 6), font=font)
        draw.text((509, 1090), nowTime.replace("-","a").replace(":","b"), (12, 0, 6), font=font)
        draw.text((509, 1243), times.replace("-","a").replace(":","b"), (12, 0, 6), font=font)
        draw.text((1395, 1188), startTime.replace("-","a").replace(":","b"), (12, 0, 6), font=font)
        fileName = 'data/pictures/cache/' + random_str() + ".png"
    elif signMode==1:
        path = "data/pictures/sign_backGround/ark/x.png"
        bg = Image.open(path)
        # merge = Image.blend(st, st2, 0.5)
        bg.paste(layer, (190, 210))
        fileName = 'data/pictures/cache/' + random_str() + ".png"
        bg.save(fileName)
        imageFile = fileName
        # 导入数据
        tp = Image.open(imageFile)

        font = ImageFont.truetype('data/fonts/Caerulaarbor.ttf', 110)
        draw = ImageDraw.Draw(tp)
        font = ImageFont.truetype('data/fonts/H-TTF-BuMing-B-2.ttf', 73)
        draw.text((2000, 716), weather, (12, 0, 6), font=font)
        draw.text((400, 1200), 'exp:', (12, 0, 6), font=font)
        draw.text((400, 900), "nowtime:", (12, 0, 6), font=font)
        draw.text((400, 1050), "totaltimes:", (12, 0, 6), font=font)
        draw.text((400, 1350), "starttime:", (12, 0, 6), font=font)
        font = ImageFont.truetype('data/fonts/Caerulaarbor.ttf', 115)
        draw.text((400, 700), id, (12, 0, 6), font=font)
        font = ImageFont.truetype('data/fonts/Caerulaarbor.ttf', 73)
        draw.text((799, 1190), exp, (12, 0, 6), font=font)
        draw.text((799, 890), nowTime.replace("-", "a").replace(":", "b"), (12, 0, 6), font=font)
        draw.text((799, 1040), times.replace("-", "a").replace(":", "b"), (12, 0, 6), font=font)
        draw.text((799, 1340), startTime.replace("-", "a").replace(":", "b"), (12, 0, 6), font=font)
        fileName = 'data/pictures/cache/' + random_str() + ".png"
    tp.save(fileName)
    return fileName

def get_user_image_url(qqid):
    return f'https://q4.qlogo.cn/g?b=qq&nk={qqid}&s=640'







