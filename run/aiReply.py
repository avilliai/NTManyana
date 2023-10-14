# -*- coding: utf-8 -*-
import asyncio
import json
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


class CListen(threading.Thread):
    def __init__(self, loop):
        threading.Thread.__init__(self)
        self.mLoop = loop

    def run(self):
        asyncio.set_event_loop(self.mLoop)  # 在新线程中开启一个事件循环

        self.mLoop.run_forever()



logger=newLogger()
with open('config/api.yaml', 'r', encoding='utf-8') as f:
    result121 = yaml.load(f.read(), Loader=yaml.FullLoader)
chatGLM_api_key=result121.get("chatGLM")
proxy=result121.get("proxy")
#读取个性化角色设定
with open('data/chatGLMCharacters.yaml', 'r', encoding='utf-8') as f:
    result2223 = yaml.load(f.read(), Loader=yaml.FullLoader)
global chatGLMCharacters
chatGLMCharacters = result2223

with open('config/chatGLM.yaml', 'r', encoding='utf-8') as f:
    result222 = yaml.load(f.read(), Loader=yaml.FullLoader)
global chatGLMapikeys
chatGLMapikeys = result222


with open('data/chatGLMData.yaml', 'r', encoding='utf-8') as f:
    cha = yaml.load(f.read(), Loader=yaml.FullLoader)
global chatGLMData
chatGLMData=cha
#logger.info(chatGLMData)
with open('config/noResponse.yaml', 'r', encoding='utf-8') as f:
    noRes1 = yaml.load(f.read(), Loader=yaml.FullLoader)
noRes=noRes1.get("noRes")


logger.info("正在启动rwkv对话模型")

logger.info("正在启动pandora_ChatGPT")
global pandoraData
with open('data/pandora_ChatGPT.yaml', 'r', encoding='utf-8') as file:
    pandoraData = yaml.load(file, Loader=yaml.FullLoader)
global totallink
totallink = False
with open('config/settings.yaml', 'r', encoding='utf-8') as f:
    result = yaml.load(f.read(), Loader=yaml.FullLoader)
master=result.get("master")
mainGroup = int(result.get("mainGroup"))
botName = result.get("botName")
trustDays=result.get("trustDays")
gptReply = result.get("gptReply")
pandoraa = result.get("pandora")
glmReply = result.get("chatGLM").get("glmReply")
trustglmReply = result.get("chatGLM").get("trustglmReply")
meta = result.get("chatGLM").get("bot_info").get("default")
context= result.get("chatGLM").get("context")
maxPrompt = result.get("chatGLM").get("maxPrompt")
allcharacters=result.get("chatGLM").get("bot_info")
turnMessage=result.get("wReply").get("turnMessage")




with open('data/userData.yaml', 'r', encoding='utf-8') as file:
    data = yaml.load(file, Loader=yaml.FullLoader)
global trustUser
global userdict
userdict = data
trustUser = []
for i in userdict.keys():
    data = userdict.get(i)
    times = int(str(data.get('sts')))
    if times > trustDays:
        trustUser.append(str(i))

logger.info('chatglm部分已读取信任用户' + str(len(trustUser)) + '个')

with open('config/chatGLMSingelUser.yaml', 'r', encoding='utf-8') as f:
    result224 = yaml.load(f.read(), Loader=yaml.FullLoader)
global chatGLMsingelUserKey
chatGLMsingelUserKey=result224
#线程预备
newLoop = asyncio.new_event_loop()
listen = CListen(newLoop)
listen.setDaemon(True)
listen.start()

'''#私聊使用chatGLM,对信任用户或配置了apiKey的用户开启
@bot.on(FriendMessage)
async def GLMFriendChat(event:FriendMessage):
    global chatGLMData,chatGLMCharacters,trustUser,chatGLMsingelUserKey,userdict
    #如果用户有自己的key
    if event.senderUin in chatGLMsingelUserKey:
        selfApiKey=chatGLMsingelUserKey.get(event.senderUin)
        #构建prompt
    #或者开启了信任用户回复且为信任用户
    elif str(event.senderUin) in trustUser and trustglmReply==True:
        logger.info("信任用户进行chatGLM提问")
        selfApiKey=chatGLM_api_key
    else:
        return
    if str(event.get_plaintext()) == "/clearGLM":
        return
    text = str(event.get_plaintext())
    logger.info("私聊glm接收消息："+text)
    # 构建新的prompt
    tep = {"role": "user", "content": text}
    # print(type(tep))
    # 获取以往的prompt
    if event.senderUin in chatGLMData:
        prompt = chatGLMData.get(event.senderUin)
        prompt.append({"role": "user", "content": text})
    # 没有该用户，以本次对话作为prompt
    else:
        prompt = [tep]
        chatGLMData[event.senderUin] = prompt
    if event.senderUin in chatGLMCharacters:
        meta1 = chatGLMCharacters.get(event.senderUin)
    else:
        logger.warning("读取meta模板")
        with open('config/settings.yaml', 'r', encoding='utf-8') as f:
            resy = yaml.load(f.read(), Loader=yaml.FullLoader)
        meta1 = resy.get("chatGLM").get("bot_info").get("default")

    try:
        setName = userdict.get(str(event.senderUin)).get("userName")
    except:
        setName = event.sender.nickname
    if setName == None:
        setName = event.sender.nickname

    meta1["user_name"] = meta1.get("user_name").replace("指挥", setName)
    meta1["user_info"] = meta1.get("user_info").replace("指挥", setName).replace("yucca",botName)
    meta1["bot_info"] = meta1.get("bot_info").replace("指挥", setName).replace("yucca",botName)
    meta1["bot_name"] = botName

    try:
        logger.info("当前meta:" + str(meta1))
        #st1 = await chatGLM(selfApiKey, meta1, prompt)
        asyncio.run_coroutine_threadsafe(asyncchatGLM(selfApiKey, meta1, prompt, event, setName, text), newLoop)

    except:
        await bot.send(event, "chatGLM启动出错，请联系master检查apiKey或重试")

# 私聊中chatGLM清除本地缓存
@bot.on(FriendMessage)
async def clearPrompt(event: FriendMessage):
    global chatGLMData
    if str(event.get_plaintext()) == "/clearGLM":
        try:
            chatGLMData.pop(event.senderUin)
            # 写入文件
            with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(chatGLMData, file, allow_unicode=True)
            await bot.send(event,"已清除近期记忆")
        except:
            await bot.send(event, "清理缓存出错，无本地对话记录")

@bot.on(FriendMessage)
async def setChatGLMKey(event: FriendMessage):
    global chatGLMsingelUserKey
    if str(event.get_plaintext()).startswith("设置密钥#"):
        key12 = str(event.get_plaintext()).split("#")[1] + ""
        try:
            prompt = [{"user": "你好"}]
            st1 = chatGLM1(key12, meta, prompt)
            #st1 = st1.replace("yucca", botName).replace("liris", str(event.sender.nickname))
            await bot.send(event, st1, True)
        except:
            await bot.send(event, "chatGLM启动出错，请联系检查apiKey或重试")
            return
        chatGLMsingelUserKey[event.senderUin] = key12
        with open('config/chatGLMSingelUser.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMsingelUserKey, file, allow_unicode=True)
        await bot.send(event, "设置apiKey成功")

@bot.on(FriendMessage)
async def setChatGLMKey(event: FriendMessage):
    global chatGLMsingelUserKey
    if str(event.get_plaintext()).startswith("取消密钥") and event.senderUin in chatGLMsingelUserKey:
        chatGLMsingelUserKey.pop(event.senderUin)
        with open('config/chatGLMSingelUser.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMsingelUserKey, file, allow_unicode=True)
        await bot.send(event, "设置apiKey成功")
#私聊设置bot角色
# print(trustUser)
@bot.on(FriendMessage)
async def showCharacter(event:FriendMessage):
    if str(event.get_plaintext())=="可用角色模板" or "角色模板" in str(event.get_plaintext()):
        st1=""
        for isa in allcharacters:
            st1+=isa+"\n"
        await bot.send(event,"对话可用角色模板：\n"+st1+"\n发送：设定#角色名 以设定角色")
@bot.on(FriendMessage)
async def setCharacter(event:FriendMessage):
    global chatGLMCharacters
    if str(event.get_plaintext()).startswith("设定#"):
        if str(event.get_plaintext()).split("#")[1] in allcharacters:

            meta1 = allcharacters.get(str(event.get_plaintext()).split("#")[1])

            try:
                setName = userdict.get(str(event.senderUin)).get("userName")
            except:
                setName = event.sender.nickname
            if setName == None:
                setName = event.sender.nickname
            meta1["user_info"] = meta1.get("user_info").replace("指挥", setName).replace("yucca", botName)
            meta1["bot_info"] = meta1.get("bot_info").replace("指挥", setName).replace("yucca", botName)
            meta1["bot_name"] = botName
            meta1["user_name"] = setName
            chatGLMCharacters[event.senderUin] = meta1

            logger.info("当前：",chatGLMCharacters)
            with open('data/chatGLMCharacters.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(chatGLMCharacters, file, allow_unicode=True)
            await bot.send(event,"设定成功")
        else:
            await bot.send(event,"不存在的角色")'''


temple = on_fullmatch(("角色模板","可用角色模板"), rule=to_me(),  priority=3, block=True)
setCharacter = on_startswith("设定#",ignorecase=False)
clearCache=on_fullmatch("/clearGLM")
chatGLMGroupRep=on_startswith("",rule=to_me())
chatGPTReply=on_startswith("/p",ignorecase=False)
chatGPTReply1=on_startswith("/chat",ignorecase=False)
xh=on_startswith("/xh")
wx=on_startswith("/wx")
rwkv=on_startswith("/rwkv")
setGLMKey=on_startswith("设置密钥#",ignorecase=False)
delGLMKey=on_startswith("取消密钥#",ignorecase=False)

try:
    subprocess.Popen(["pandora", "-t", "config/token.txt","-s", "127.0.0.1:23459", "-p", proxy])
except:
    logger.error("pandora启动失败")



#群内chatGLM回复
@chatGLMGroupRep.handle()
async def handle_receive(bot: Bot, event: MessageEvent):
    global trustUser, chatGLMapikeys,chatGLMData,chatGLMCharacters,chatGLMsingelUserKey,userdict
    if gptReply == True:

        asyncio.run_coroutine_threadsafe(askGPTT(Bot,event),newLoop)

    elif glmReply == True or (trustglmReply == True and str(event.senderUin) in trustUser) or event.senderUin in chatGLMsingelUserKey:
        text = str(event.get_plaintext()).replace("@" + str(bot.qq) + "", '').replace(" ","")
        logger.info("分支1")
        for saa in noRes:
            if text==saa:
                logger.warning("与屏蔽词匹配，chatGLM不回复")
                return
        if text=="" or text==" ":
            text="在吗"
        #构建新的prompt
        tep={"role": "user","content": text}
        #print(type(tep))
        #获取以往的prompt
        if event.senderUin in chatGLMData and context==True:
            prompt=chatGLMData.get(event.senderUin)
            prompt.append({"role": "user","content": text})

        #没有该用户，以本次对话作为prompt
        else:
            prompt=[tep]
            chatGLMData[event.senderUin] =prompt
        #logger.info("当前prompt"+str(prompt))

        if event.senderUin in chatGLMsingelUserKey:
            logger.info("自有apiKey用户进行提问")
            selfApiKey = chatGLMapikeys.get(event.senderUin)
            # 构建prompt
        # 或者开启了信任用户回复且为信任用户
        elif str(event.senderUin) in trustUser and trustglmReply == True:
            logger.info("信任用户进行chatGLM提问")
            selfApiKey = chatGLM_api_key
        else:
            selfApiKey = chatGLM_api_key

        #获取角色设定
        if event.senderUin in chatGLMCharacters:
            meta1=chatGLMCharacters.get(event.senderUin)
        else:
            logger.warning("读取meta模板")
            with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                resy = yaml.load(f.read(), Loader=yaml.FullLoader)
            meta1 = resy.get("chatGLM").get("bot_info").get("default")
        try:
            setName = userdict.get(str(event.senderUin)).get("userName")
        except:
            setName = event.sendMemberName
        if setName == None:
            setName = event.sendMemberName
        meta1["user_name"] = meta1.get("user_name").replace("指挥", setName)
        meta1["user_info"] = meta1.get("user_info").replace("指挥", setName).replace("yucca",botName)
        meta1["bot_info"]=meta1.get("bot_info").replace("指挥",setName).replace("yucca",botName)
        meta1["bot_name"]=botName

        logger.info("chatGLM接收提问:" + text)
        try:
            logger.info("当前meta:"+str(meta1))
            asyncio.run_coroutine_threadsafe(asyncchatGLM(bot,selfApiKey, meta1, prompt, event, setName, text), newLoop)
            #st1 = await chatGLM(selfApiKey, meta1, prompt)


        except:
            await bot.send(event, "chatGLM启动出错，请联系master检查apiKey或重试")
    elif (str(event.peerUin) == str(mainGroup) and chatGLM_api_key!="sdfafjsadlf;aldf") or (event.peerUin in chatGLMapikeys)  :
        text = str(event.get_plaintext()).replace("@" + str(bot.qq) + "", '').replace(" ","")
        logger.info("分支2")
        for saa in noRes:
            if text==saa:
                logger.warning("与屏蔽词匹配，chatGLM不回复")
                return
        if text=="" or text==" ":
            text="在吗"
        # 构建新的prompt
        tep = {"role": "user", "content": text}

        # 获取以往的prompt
        if event.senderUin in chatGLMData and context==True:
            prompt = chatGLMData.get(event.senderUin)
            prompt.append({"role": "user","content": text})
        # 没有该用户，以本次对话作为prompt
        else:
            prompt = [tep]
            chatGLMData[event.senderUin] = prompt
        #logger.info("当前prompt" + str(prompt))
        #获取专属meta
        if event.senderUin in chatGLMCharacters:
            meta1=chatGLMCharacters.get(event.senderUin)
        else:
            logger.warning("读取meta模板")
            with open('config/settings.yaml', 'r', encoding='utf-8') as f:
                resy = yaml.load(f.read(), Loader=yaml.FullLoader)
            meta1 = resy.get("chatGLM").get("bot_info").get("default")
        try:
            setName = userdict.get(str(event.senderUin)).get("userName")
        except:
            setName = event.sendMemberName
        if setName==None:
            setName = event.sendMemberName
        meta1["user_name"] = meta1.get("user_name").replace("指挥", setName)
        meta1["user_info"] = meta1.get("user_info").replace("指挥", setName).replace("yucca",botName)
        meta1["bot_info"] = meta1.get("bot_info").replace("指挥", setName).replace("yucca",botName)
        meta1["bot_name"] = botName

        logger.info("chatGLM接收提问:" + text)
        #获取apiKey
        logger.info("当前meta:"+str(meta1))
        if str(event.peerUin) == str(mainGroup):
            key1 = chatGLM_api_key
        else:
            key1 = chatGLMapikeys.get(event.peerUin)
        try:


            #分界线
            asyncio.run_coroutine_threadsafe(asyncchatGLM(bot,key1, meta1, prompt,event,setName,text), newLoop)
        except:
            await bot.send(event, "chatGLM启动出错，请联系master检查apiKey或重试")
#用于chatGLM清除本地缓存
@clearCache.handle()
async def clearPrompt(bot: Bot, event: MessageEvent):
    global chatGLMData
    try:
        chatGLMData.pop(event.senderUin)
        # 写入文件
        with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMData, file, allow_unicode=True)
        await bot.send(event,"已清除近期记忆")
    except:
        await bot.send(event,"清理缓存出错，无本地对话记录")

@setGLMKey.handle()
async def setChatGLMKey(bot: Bot, event: MessageEvent):
    global chatGLMapikeys,chatGLMsingelUserKey
    key12=str(event.get_plaintext()).split("#")[1]+""
    try:

        prompt=[{"user":"你好"}]
        st1 = chatGLM1(key12, meta,prompt)
        #asyncio.run_coroutine_threadsafe(asyncchatGLM(key1, meta1, prompt, event, setName, text), newLoop)
        st1 = st1.replace("yucca", botName).replace("liris", str(event.sendMemberName))
        await bot.send(event, st1)
    except:
        await bot.send(event, "chatGLM启动出错，请联系检查apiKey或重试")
        return
    #logger.info(chatGLMapikeys)
    if event.is_group:
        logger.info("群聊"+str(event.peerUin)+"设置了新的apiKey" + key12)
        chatGLMapikeys[event.peerUin]=key12
        with open('config/chatGLM.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMapikeys, file, allow_unicode=True)
        #await bot.send(event, "设置apiKey成功")

    chatGLMsingelUserKey[event.senderUin]=key12
    with open('config/chatGLMSingelUser.yaml', 'w', encoding="utf-8") as file:
        yaml.dump(chatGLMsingelUserKey, file, allow_unicode=True)
    await bot.send(event, "设置apiKey成功")

@delGLMKey.handle()
async def setChatGLMKey(bot: Bot, event: MessageEvent):
    global chatGLMapikeys
    if event.peerUin in chatGLMapikeys:
        chatGLMapikeys.pop(event.peerUin)
        with open('config/chatGLM.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMapikeys, file, allow_unicode=True)
        await bot.send(event, "取消apiKey成功")
        
@chatGPTReply.handle()
async def pandoraSever(bot: Bot, event: MessageEvent):
    global pandoraData
    if pandoraa:
        #await bot.send(event,"请等待")
        sf=asyncio.run_coroutine_threadsafe(askGPTT(bot,event), newLoop)
        await bot.send(event,sf.result())
    else:
        await bot.send(event, "当前未启用pandora_chatGPT")

@chatGPTReply1.handle()
async def gpt3(bot: Bot, event: MessageEvent):

    s = str(event.get_plaintext()).replace("/chat", "")
    try:
        logger.info("gpt3.5接收信息：" + s)
        url = "https://api.lolimi.cn/API/AI/mfcat3.5.php?sx=你是一个可爱萝莉&msg="+s+"&type=json"
        async with httpx.AsyncClient(timeout=40) as client:
            # 用get方法发送请求
            response = await client.get(url=url)
        s=response.json().get("data")

        logger.info("gpt3.5:" + s)
        await bot.send(event, s)
    except:
        logger.error("调用gpt3.5失败，请检查网络或重试")
        await bot.send(event, "无法连接到gpt3.5，请检查网络或重试")
#科大讯飞星火ai
@xh.handle()
async def gpt3(bot: Bot, event: MessageEvent):

    s = str(event.get_plaintext()).replace("/xh", "")
    try:
        logger.info("讯飞星火接收信息：" + s)
        url = "https://api.lolimi.cn/API/AI/xh.php?msg=" + s
        async with httpx.AsyncClient(timeout=40) as client:
            # 用get方法发送请求
            response = await client.get(url=url)
        s = response.json().get("data").get("output")

        logger.info("讯飞星火:" + s)
        await bot.send(event, s)
    except:
        logger.error("调用讯飞星火失败，请检查网络或重试")
        await bot.send(event, "无法连接到讯飞星火，请检查网络或重试")

# 文心一言
@wx.handle()
async def gpt3(bot: Bot, event: MessageEvent):

    s = str(event.get_plaintext()).replace("/wx", "")
    try:
        logger.info("文心一言接收信息：" + s)
        url = "https://api.lolimi.cn/API/AI/wx.php?msg=" + s
        async with httpx.AsyncClient(timeout=40) as client:
            # 用get方法发送请求
            response = await client.get(url=url)
        s = response.json().get("data").get("output")

        logger.info("文心一言:" + s)
        await bot.send(event, s)
    except:
        logger.error("调用文心一言失败，请检查网络或重试")
        await bot.send(event, "无法连接到文心一言，请检查网络或重试")

@rwkv.handle()
async def rwkv(bot: Bot, event: MessageEvent):
    s = str(event.get_plaintext()).replace("/rwkv", "")
    try:
        logger.info("rwkv接收信息：" + s)
        s = await rwkvHelper(s)
        logger.info("rwkv:" + s)
        await bot.send(event, s)
    except:
        logger.error("调用rwkv失败，请检查本地rwkv是否启动或端口是否配置正确(8000)")
        await bot.send(event, "无法连接到本地rwkv")

async def askGPTT(bot,event):
    global trustUser, chatGLMapikeys, chatGLMData, chatGLMCharacters, chatGLMsingelUserKey, userdict
    prompt = str(event.get_plaintext()).replace("/p","")

    message_id = str(uuid.uuid4())
    model = "text-davinci-002-render-sha"
    logger.info("ask:" + prompt)
    if event.peerUin in pandoraData.keys():
        pub = event.peerUin
        conversation_id = pandoraData.get(event.peerUin).get("conversation_id")
        parent_message_id = pandoraData.get(event.peerUin).get("parent_message_id")
    else:
        if len(pandoraData.keys()) < 10:
            pub = event.peerUin
            conversation_id = None
            parent_message_id = "f0bf0ebe-1cd6-4067-9264-8a40af76d00e"
        else:
            try:
                pub = random.choice(pandoraData.keys())
                conversation_id = pandoraData.get(pub).get("conversation_id")
                parent_message_id = pandoraData.get(pub).get("parent_message_id")
            except:
                await bot.send_group_message(event.peerUin, "当前服务器负载过大，请稍后再试")
                return

    try:
        loop = asyncio.get_event_loop()
        # 使用 loop.run_in_executor() 方法来将同步函数转换为异步非阻塞的方式进行处理
        # 第一个参数是执行器，可以是 None、ThreadPoolExecutor 或 ProcessPoolExecutor
        # 第二个参数是同步函数名，后面跟着任何你需要传递的参数
        # result=chatGLM(apiKey,bot_info,prompt)
        parent_message_id, conversation_id, response_message = await loop.run_in_executor(None, ask_chatgpt, prompt, model, message_id,parent_message_id,conversation_id)

        logger.info("answer:" + response_message)
        logger.info("conversation_id:" + conversation_id)
        #await bot.send_group_message(event.peerUin, response_message)
        pandoraData[pub] = {"parent_message_id": parent_message_id, "conversation_id": conversation_id}
        with open('data/pandora_ChatGPT.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(pandoraData, file, allow_unicode=True)
        return response_message
    except:
        return "当前服务器负载过大，请稍后再试"
        #await bot.send(event, "当前服务器负载过大，请稍后再试")





#CharacterchatGLM部分
def chatGLM(api_key,bot_info,prompt,model1):
    logger.info("当前模式:"+model1)
    zhipuai.api_key = api_key
    if model1=="chatglm_pro":
        response = zhipuai.model_api.sse_invoke(
            model="chatglm_pro",
            prompt=prompt,
            temperature=0.95,
            top_p=0.7,
            incremental=True
        )
    elif model1=="chatglm_std":
        response = zhipuai.model_api.sse_invoke(
            model="chatglm_std",
            prompt=prompt,
            temperature=0.95,
            top_p=0.7,
            incremental=True
        )
    elif model1=="chatglm_lite":
        response = zhipuai.model_api.sse_invoke(
            model="chatglm_lite",
            prompt=prompt,
            temperature=0.95,
            top_p=0.7,
        )
    else:
        response = zhipuai.model_api.sse_invoke(
            model="characterglm",
            meta= bot_info,
            prompt= prompt,
            incremental=True
        )
    str1=""
    for event in response.events():
      if event.event == "add":
          str1+=event.data
          #print(event.data)
      elif event.event == "error" or event.event == "interrupted":
          str1 += event.data
          #print(event.data)
      elif event.event == "finish":
          str1 += event.data
          #print(event.data)
          print(event.meta)
      else:
          str1 += event.data
          #print(event.data)
    #print(str1)
    return str1
# 创建一个异步函数
async def asyncchatGLM(bot,apiKey,bot_info,prompt,event,setName,text):
    global chatGLMData

    loop = asyncio.get_event_loop()
    # 使用 loop.run_in_executor() 方法来将同步函数转换为异步非阻塞的方式进行处理
    # 第一个参数是执行器，可以是 None、ThreadPoolExecutor 或 ProcessPoolExecutor
    # 第二个参数是同步函数名，后面跟着任何你需要传递的参数
    #result=chatGLM(apiKey,bot_info,prompt)
    model1 = result.get("chatGLM").get("model")
    st1 = await loop.run_in_executor(None, chatGLM,apiKey,bot_info,prompt,model1)
    # 打印结果
    #print(result)
    st11 = st1.replace(setName, "指挥")

    await bot.send(event, st1)
    if len(st1) > 670:
        await bot.send(event, "system:当前prompt过长，将不记录本次回复\n建议发送 /clearGLM 以清除聊天内容")
        try:
            prompt.remove(prompt[-1])
            chatGLMData[event.senderUin]=prompt
        except:
            logger.error("chatGLM删除上一次对话失败")
        return

    logger.info("chatGLM:" + st1)
    if turnMessage==True and event.type=='FriendMessage' and event.senderUin!=master:
        await bot.send_friend_message(int(master),"chatGLM接收消息：\n来源:"+str(event.senderUin)+"\n提问:"+text+"\n回复:"+st1)
    try:
        addStr = '添加' + text + '#' + st11
        mohuaddReplys(addStr, str("chatGLMReply"))
    except:
        logger.error("写入本地词库失败")
    if context == True:
        # 更新该用户prompt
        prompt.append({"role": "assistant", "content": st1})
        # 超过10，移除第一个元素

        if len(prompt) > maxPrompt:
            logger.error("glm prompt超限，移除元素")
            del prompt[0]
            del prompt[0]
        chatGLMData[event.senderUin] = prompt
        # 写入文件
        with open('data/chatGLMData.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(chatGLMData, file, allow_unicode=True)


# 运行异步函数




