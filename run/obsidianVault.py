# -*- coding: utf-8 -*-
import asyncio
import json
import os.path
import random
import subprocess
import uuid
from asyncio import sleep

import httpx
#import poe
import yaml
import threading
from asyncio import sleep

import zhipuai
from nonebot.params import CommandArg

from plugins.PandoraChatGPT import ask_chatgpt
from plugins.RandomStr import random_str
from plugins.chatGLMonline import chatGLM1
from plugins.newLogger import newLogger

from plugins.rwkvHelper import rwkvHelper
from plugins.wReply.mohuReply import mohuaddReplys
from pathlib import Path

from nonebot import on_command, on_fullmatch, on_startswith
from nonebot.adapters.red import Bot
from nonebot.adapters.red.event import MessageEvent
from nonebot.adapters.red.message import MessageSegment, Message
from nonebot.rule import to_me, startswith

order1=on_startswith("pdf ")
order2=on_startswith("ls")

with open('config/settings.yaml', 'r', encoding='utf-8') as f:
    settings = yaml.load(f.read(), Loader=yaml.FullLoader)
obsidianVault=settings.get("obsidianVault")
@order1.handle()
async def addSUB(bot: Bot, event: MessageEvent):
    pa=obsidianVault+"/"+event.get_plaintext().replace("pdf ","")
    if os.path.exists(pa):
        print(pa)
        import aspose.words as aw

        # 加载现有的 Markdown 文档
        doc = aw.Document(obsidianVault+"/"+event.get_plaintext().replace("pdf ",""))
        saveOptions = aw.saving.PdfSaveOptions()
        saveOptions.compliance = aw.saving.PdfCompliance.PDF17
        # 将文档另存为 PDF
        path="data/pictures/cache/"+random_str()+".pdf"
        doc.save(path)
        print("over")
        fil=open(path,"rb")
        sfa=fil.read()

        await bot.upload(file=sfa)
        fil.close()
@order2.handle()
async def addSUB(bot: Bot, event: MessageEvent):
    ass=os.listdir(obsidianVault+event.get_plaintext().replace("ls",""))
    await bot.send(event,str(ass).replace(",","\n").replace("，","\n"))