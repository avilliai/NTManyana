import asyncio
import json
import subprocess
import time
from asyncio import sleep
from pathlib import Path

import httpx
import nonebot
import yaml
from PIL import Image
from nonebot import on_command, on_fullmatch, on_startswith
from nonebot.adapters.red import Bot
from nonebot.adapters.red.api.model import ChatType
from nonebot.adapters.red.event import MessageEvent
from nonebot.adapters.red.message import MessageSegment, ForwardNode, Message
from nonebot.params import EventToMe
from nonebot.rule import to_me

from plugins.RandomStr import random_str
from plugins.webScreenShoot import BiliDynamicsScreen

addSub=on_startswith("/sub bili ")
cancelSub=on_startswith("/unsub bili ")
needaBot=on_startswith("")
global five_minutes_later_timestamp
five_minutes_later_timestamp=""
with open('data/biliMonitor.yaml', 'r', encoding='utf-8') as f:
    BiliTasks = yaml.load(f.read(), Loader=yaml.FullLoader)
with open('config/settings.yaml', 'r', encoding='utf-8') as f:
    settings = yaml.load(f.read(), Loader=yaml.FullLoader)
waitTime=settings.get("UpdateTime")
@addSub.handle()
async def addSUB(bot: Bot, event: MessageEvent):
    try:
        uid = int(event.get_plaintext().split(" ")[-1])
        if uid in BiliTasks:
            sa=BiliTasks.get(uid).get("group")
            sa.append(int(event.peerUin))
            BiliTasks[uid]["group"] = sa
        else:
            lat = await bilidynamics(uid)
            BiliTasks[uid] = {"group": [int(event.peerUin)], "latestDynamics": lat}
        with open('data/biliMonitor.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(BiliTasks, file, allow_unicode=True)
        await bot.send(event, "添加uid订阅成功")
    except:
        await bot.send(event, "无效的uid")
@cancelSub.handle()
async def UnSUB(bot: Bot, event: MessageEvent):
    try:
        uid = int(event.get_plaintext().split(" ")[-1])
        if uid in BiliTasks:
            sa = BiliTasks.get(uid).get("group")
            sa.remove(int(event.peerUin))
            BiliTasks[uid]["group"] = sa
        else:
            await bot.send(event, "无效的uid,本群未创建该订阅任务")

            return
        with open('data/biliMonitor.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(BiliTasks, file, allow_unicode=True)
        await bot.send(event, "移除uid订阅成功")
    except:
        await bot.send(event, "无效的uid")

@needaBot.handle()
async def dynamicsMonitor(bot: Bot, event: MessageEvent):
    global five_minutes_later_timestamp
    current_timestamp = time.time()
    # 在当前的时间戳上加上300秒，即五分钟
    if five_minutes_later_timestamp=="" or current_timestamp>five_minutes_later_timestamp:
        print("开始检测")
        five_minutes_later_timestamp = current_timestamp + waitTime
        for i in BiliTasks.keys():
            lat = await bilidynamics(i)
            if lat != BiliTasks.get(i).get("latestDynamics"):

                groups = BiliTasks.get(i).get("group")
                url = "https://t.bilibili.com/" + str(lat)
                try:
                    pat = await BiliDynamicsScreen(url, "data/pictures/cache/" + random_str() + ".png")
                    oll=0
                except:
                    oll=1
                if oll==0:
                    BiliTasks[i]["latestDynamics"] = lat
                    with open('data/biliMonitor.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(BiliTasks, file, allow_unicode=True)
                for iss in groups:
                    try:
                        await bot.send_message(chat_type=ChatType(2),target=iss, message=MessageSegment.image(Path(pat)))
                    except:
                        print("发送失败")







async def bilidynamics(uid):
    # 向本地 API 发送 POST 请求
    url = 'http://localhost:9081/synthesize'
    data = json.dumps({"uid": uid})
    try:
        async with httpx.AsyncClient(timeout=200) as client:
            dynamic_id = await client.post(url, json=data)
            print(dynamic_id.json(), type(dynamic_id))
            return dynamic_id.json().get("dynamic_id")
    except Exception as e:
        print(e)

subprocess.Popen(["python.exe", "biliDynamic.py"], cwd="plugins")
