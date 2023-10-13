from pathlib import Path
from typing import Annotated

from nonebot import on_command, on_fullmatch, on_startswith
from nonebot.adapters.red import Bot
from nonebot.adapters.red.event import MessageEvent
from nonebot.adapters.red.message import MessageSegment
from nonebot.params import EventToMe
from nonebot.rule import to_me

Menu = on_fullmatch(("帮助","菜单","help"), rule=to_me(),  priority=10, block=True)
'''chatGLMGroupRep=on_startswith("/p")
@chatGLMGroupRep.handle()
async def sfds(bot: Bot, event: MessageEvent):
    print("1")
    print(event.json().get("message").get("data").get("text"))
    await bot.send(event,"hello")'''
@Menu.handle()
async def handle_receive(bot: Bot, event: MessageEvent):
    if event.is_group:
        print(event.sendMemberName)
        print(event.senderUin)
        print(event.peerUin)
        print(event.get_plaintext())
        #await bot.send_group_message(event.scene, MessageSegment.image(Path("data/help1.png")))