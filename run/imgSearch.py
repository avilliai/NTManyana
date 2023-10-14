# -*- coding: utf-8 -*-
import asyncio
import json
import os
import datetime
import random
import time
import sys
import socket
from io import BytesIO
from pathlib import Path

import httpx
import requests

import yaml
from PIL import Image
from nonebot.adapters.red.api.model import ChatType

from plugins.RandomStr import random_str
from plugins.imgSearch import test2, superSearch, test1, test, saucenoS


from plugins.newLogger import newLogger
from plugins.translater import translate
from nonebot import on_command, on_fullmatch, on_startswith, on_keyword, on_regex, on_endswith
from nonebot.adapters.red import Bot
from nonebot.adapters.red.event import MessageEvent
from nonebot.adapters.red.message import MessageSegment, Message

#指令区
searchImg1=on_fullmatch("搜图")
searchImg2=on_startswith("") #为了处理 搜图[图片] 和 搜图 两种情况，设置成对所有消息触发


#拿数据
logger=newLogger()
logger.info("搜图功能启动完毕")
with open('config/api.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
api_key=result.get("sauceno-api")
cookies=result.get("e-hentai")
proxy=result.get("proxy")
global dataGet
dataGet={}
global userSearch
@searchImg1.handle()
async def startYourSearch(bot: Bot, event: MessageEvent):
    global dataGet
    if str(event.get_plaintext())=="搜图":
        await bot.send(event,"请发送要搜索的图片")
        dataGet[int(event.senderUin)]=[]
@searchImg2.handle()
async def imgSearcher(bot: Bot, event: MessageEvent):
    global dataGet
    if ("搜图" in str(event.get_plaintext() and "img" in event.json()) or int(event.senderUin) in dataGet):
        pat=""
        for i in event.original_message:
            print(i)
            if i.type=="image":
                #print("打印path")
                logger.info("获取到path="+i.data.get("path"))
                pat=i.data.get("path").replace(r"\\","/")
                logger.warning(pat)
        if pat=="":
            return
        s = await bot.fetch_media(event.msgId, ChatType(2), event.peerUid, event.elements[0].elementId, 0, 2)
        img = Image.open(BytesIO(s))  # 从二进制数据创建图片对象
        pat = "data/pictures/cache/" + random_str() + ".png"
        img.save(pat)
        logger.info("接收来自群："+str(int(event.peerUin))+" 用户："+str(int(event.senderUin))+" 的搜图指令")
        dataGet[int(event.senderUin)]=[]

        img_url = pat

        # Replace the key with your own
        logger.info("发起搜图请求")
        await bot.send(event,"正在检索....请稍候")
        #sauceno搜图


        try:
            result, piccc = await saucenoS(url=img_url, api_key=api_key,proxies=proxy)
            #logger.info("sauceno获取到结果：" + result)

            dataGet.get(int(event.senderUin)).append(result)
            dataGet.get(int(event.senderUin)).append(MessageSegment.image(Path(piccc)))
                #await bot.send(event,' similarity:'+str(response.json().get("results")[0].get('header').get('similarity'))+"\n"+str(response.json().get("results")[0].get('data')).replace(",","\n").replace("{"," ").replace("}","").replace("'","").replace("[","").replace("]",""),True)
        except:
            logger.error("sauceno搜图失败")

        #使用TraceMoe搜图
        try:
            result,piccc=await test(url=img_url,proxies=proxy)
            #logger.info("TraceMoe获取到结果：" +result)
            dataGet.get(int(event.senderUin)).append(result)
            dataGet.get(int(event.senderUin)).append(MessageSegment.image(Path(piccc)))
            # await bot.send(event,' similarity:'+str(response.json().get("results")[0].get('header').get('similarity'))+"\n"+str(response.json().get("results")[0].get('data')).replace(",","\n").replace("{"," ").replace("}","").replace("'","").replace("[","").replace("]",""),True)
        except:
            logger.error("TraceMoe搜图失败，无结果或访问次数过多，请稍后再试")

            # b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",message_chain=MessageChain([result, Image(url=urlss]))
            #dataGet.get(int(event.senderUin)).append("TraceMoe搜图失败，无结果或访问次数过多，请稍后再试")
        #使用Ascii2D
        try:
            result,piccc=await test1(url=img_url,proxies=proxy)
            #logger.info("Ascii2D获取到结果：\n" +result)
            dataGet.get(int(event.senderUin)).append(result)
            dataGet.get(int(event.senderUin)).append(MessageSegment.image(Path(piccc)))
            # await bot.send(event,' similarity:'+str(response.json().get("results")[0].get('header').get('similarity'))+"\n"+str(response.json().get("results")[0].get('data')).replace(",","\n").replace("{"," ").replace("}","").replace("'","").replace("[","").replace("]",""),True)
        except:
            logger.error("Ascii2D搜图失败，无结果或访问次数过多，请稍后再试")

            # b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",message_chain=MessageChain([result, Image(url=urlss]))
            #dataGet.get(int(event.senderUin)).append("Ascii2D搜图失败，无结果或访问次数过多，请稍后再试")

        # 使用IQDB
        try:
            result, piccc = await superSearch(url=img_url, proxies=proxy)
            logger.info("iqdb获取到结果：\n" + result)
            dataGet.get(int(event.senderUin)).append(result)
            dataGet.get(int(event.senderUin)).append(MessageSegment.image(Path(piccc)))
            # await bot.send(event,' similarity:'+str(response.json().get("results")[0].get('header').get('similarity'))+"\n"+str(response.json().get("results")[0].get('data')).replace(",","\n").replace("{"," ").replace("}","").replace("'","").replace("[","").replace("]",""),True)
        except:
            logger.error("iqdb搜图失败，无结果或访问次数过多，请稍后再试")
            #dataGet.get(int(event.senderUin)).append(result)
            # b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",message_chain=MessageChain([result, Image(url=urlss]))
            #dataGet.get(int(event.senderUin)).append("iqdb搜图失败，无结果或访问次数过多，请稍后再试")
        # 使用E-hentai
        try:
            result, piccc = await test2(url=img_url, proxies=proxy,cookies=cookies)
            logger.info("E-hentai获取到结果：" + result)
            dataGet.get(int(event.senderUin)).append(result)
            dataGet.get(int(event.senderUin)).append(MessageSegment.image(Path(piccc)))
            # await bot.send(event,' similarity:'+str(response.json().get("results")[0].get('header').get('similarity'))+"\n"+str(response.json().get("results")[0].get('data')).replace(",","\n").replace("{"," ").replace("}","").replace("'","").replace("[","").replace("]",""),True)
        except:
            logger.error("E-hentai搜图失败，无结果或访问次数过多，请稍后再试")
            #dataGet.get(int(event.senderUin)).append(result)
            # b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",message_chain=MessageChain([result, Image(url=urlss]))
            # dataGet.get(int(event.senderUin)).append("iqdb搜图失败，无结果或访问次数过多，请稍后再试")'''
        await bot.send(event,(dataGet.get(int(event.senderUin))))
        dataGet.pop(int(event.senderUin))


