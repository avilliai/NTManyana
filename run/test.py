import json
from io import BytesIO
from pathlib import Path
from typing import Annotated

import yaml
from PIL import Image
from nonebot import on_command, on_fullmatch, on_startswith
from nonebot.adapters.red import Bot
from nonebot.adapters.red.api.model import ChatType
from nonebot.adapters.red.event import MessageEvent
from nonebot.adapters.red.message import MessageSegment, ForwardNode, Message
from nonebot.params import EventToMe
from nonebot.rule import to_me

addSub=on_startswith("/sub bilibili ")
cancelSub=on_startswith("/unsub bilibli")

with open('data/biliMonitor.yaml', 'r', encoding='utf-8') as f:
    BiliTasks = yaml.load(f.read(), Loader=yaml.FullLoader)
@addSub.handle()
async def addSUB(bot: Bot, event: MessageEvent):
    try:
        uid = int(event.get_plaintext().split(" ")[-1])
        if uid in BiliTasks:
            BiliTasks[uid]["group"] = BiliTasks.get(uid).get("group").append(int(event.peerUin))
        else:
            dat = await dynamicsCount(uid)
            BiliTasks[uid] = {"group": [int(event.peerUin)], "totalDynamics": dat}
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
async def dynamicsCount(uid):
    return 1
Menu = on_startswith("/")
'''chatGLMGroupRep=on_startswith("/p")
@chatGLMGroupRep.handle()
async def sfds(bot: Bot, event: MessageEvent):
    print("1")
    print(event.json().get("message").get("data").get("text"))
    await bot.send(event,"hello")'''
@Menu.handle()
async def handle_receive(bot: Bot, event: MessageEvent):
    print(event.get_plaintext())
    if "image" in event.json():
        print(event.json())

        print(event.elements)

        s=await bot.fetch_media(event.msgId,ChatType(2),event.peerUid,event.elements[1].elementId,0,2)
        img = Image.open(BytesIO(s))  # 从二进制数据创建图片对象
        path = "1.png"
        img.save(path)
        '''if int(event.senderUin)==1840094972:

            print(event.sendMemberName)
            print(event.senderUin)
            print(event.peerUin)
            print(event.get_plaintext())
            print(event.sendType)
            b1=ForwardNode(uin=bot.self_id,name="Manyana",group=event.peerUin,message=Message("你好"))
            b2=ForwardNode(uin=bot.self_id,name="Manyana",group=event.peerUin,message=Message("你好"))

            await bot.send(event,(["你好",MessageSegment.image(Path("config/help1.png")),"你好",MessageSegment.image(Path("config/help1.png"))]))
            await bot.send_fake_forward(target="732096208",chat_type=ChatType(2),nodes=[b1,b2],source_chat_type=ChatType(2),source_target="3552663628")'''


            #await bot.send_group_message(event.scene, MessageSegment.image(Path("data/help1.png")))