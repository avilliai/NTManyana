import asyncio
import random
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image
from PicImageSearch import Network, TraceMoe, Ascii2D, Iqdb, Google, EHentai, SauceNAO
from PicImageSearch.model import Ascii2DResponse, IqdbResponse, TraceMoeResponse, GoogleResponse, EHentaiResponse

from plugins.RandomStr import random_str
from plugins.newLogger import newLogger

proxies = "http://127.0.0.1:1080"
#proxies = None
url = 'https://i.pixiv.re/img-master/img/2023/06/22/18/18/45/109241038_p0_master1200.jpg'


async def test(url,proxies):
    async with Network(proxies=proxies) as client:
        tracemoe = TraceMoe(client=client, mute=False, size=None)
        #resp = await tracemoe.search(url=url)
        resp = await tracemoe.search(file=url.replace(r"\\","/"))
        sf="相似度："+str(resp.raw[0].similarity)+"\n名称："+str(resp.raw[0].title_romaji)+"/"+str(resp.raw[0].title_english)+"/"+str(resp.raw[0].title_chinese)+"\n源文件："+str(resp.raw[0].filename)+"\n链接1："+str(resp.raw[0].image)+"\n链接2:"+str(resp.raw[0].video)
        #返回数据与封面
        proxie2 = {
            "http://": proxies,
            "https://": proxies
        }
        try:
            async with httpx.AsyncClient(proxies=proxie2, timeout=20, headers=get_headers()) as client:
                url = str(resp.raw[0].cover_image)
                r = await client.get(url)
                img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
                path = "data/pictures/cache/" + random_str() + ".png"
                img.save(path)
        except:
            path="data/autoReply/imageReply/axaAaRaUaaafa7a.png"
        return "traceMoe获取到结果："+sf+"\n============",path
async def test1(url,proxies):
    bovw = True  # 是否使用特征检索
    verify_ssl = True  # 是否校验 SSL 证书
    async with Network(proxies=proxies,verify_ssl=verify_ssl) as client:
        ascii2d = Ascii2D(client=client, bovw=bovw)
        #resp = await ascii2d.search(url=url)
        resp = await ascii2d.search(file=url.replace(r"\\","/"))
        #show_result(resp)
        selected = next((i for i in resp.raw if i.title or i.url_list), resp.raw[0])
        # logger.info(selected.origin)
        #print("================")
        fs="标题："+str(selected.title)+"\n作者:"+str(selected.author)+"\n作者链接:"+str(selected.author_url)+"\n作品页:"+str(selected.url)
        #print(fs)
        proxie2 = {
            "http://": proxies,
            "https://": proxies
        }
        try:
            async with httpx.AsyncClient(proxies=proxie2, timeout=20, headers=get_headers()) as client:
                url = selected.thumbnail
                r = await client.get(url)
                img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
                path = "data/pictures/cache/" + random_str() + ".png"
                img.save(path)
        except:
            path="data/autoReply/imageReply/axaAaRaUaaafa7a.png"
        return "ascii2D获取到结果"+fs+"\n============",path


async def superSearch(url,proxies):
    async with Network(proxies=proxies) as client:
        iqdb = Iqdb(client=client)
        #resp = await iqdb.search(url=url)
        print("=====================")
        print(url)
        resp = await iqdb.search(file=url.replace(r"\\","/"))
        fs=f"模式: {resp.raw[0].content}"+"\n"+f"来源地址: {resp.raw[0].url}"+"\n"+f"相似度: {resp.raw[0].similarity}"+"\n"+f"图片大小: {resp.raw[0].size}"+"\n"+f"图片来源: {resp.raw[0].source}"+"\n"+f"其他图片来源: {resp.raw[0].other_source}"+"\n"+f"SauceNAO搜图链接: {resp.saucenao_url}"+"\n"+f"Ascii2d搜图链接: {resp.ascii2d_url}"+"\n"+f"TinEye搜图链接: {resp.tineye_url}"+"\n"+f"Google搜图链接: {resp.google_url}"
        #print(fs)
        proxie2 = {
            "http://": proxies,
            "https://": proxies
        }
        try:
            async with httpx.AsyncClient(proxies=proxie2, timeout=20, headers=get_headers()) as client:
                url = str(resp.raw[0].thumbnail)
                r = await client.get(url)
                img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
                path = "data/pictures/cache/" + random_str() + ".png"
                img.save(path)
        except:
            path="data/autoReply/imageReply/axaAaRaUaaafa7a.png"
        return "iqdb获取到结果："+fs+"\n============",path

async def test2(url,proxies,cookies):
    #cookies = 'ipb_session_id=bc4e5da825b5ad5325688bd5d6d5c21d; ipb_member_id=7584785; ipb_pass_hash=8e9aa8e90a14b059ba8ee70075120c17; sk=mua8zab26lmwo63gkcydsht8kslv'  # 注意：如果要使用 EXHentai 搜索，需要提供 cookies
    #cookies='ipb_member_id=7584785; ipb_pass_hash=8e9aa8e90a14b059ba8ee70075120c17; ipb_coppa=0; sk=mua8zab26lmwo63gkcydsht8kslv; ipb_session_id=538204ee280a418b7caa0a089a673f56'
    ex = True  # 是否使用 EXHentai 搜索，推荐用 bool(cookies) ，即配置了 cookies 就使用 EXHentai 搜索
    timeout = 60  # 尽可能避免超时返回空的 document
    async with Network(proxies=proxies, cookies=cookies, timeout=timeout) as client:
        ehentai = EHentai(client=client)
        #resp = await ehentai.search(url=url, ex=ex)
        resp = await ehentai.search(file=url.replace(r"\\","/"), ex=ex)
        proxie2 = {
            "http://": proxies,
            "https://": proxies
        }
        try:
            async with httpx.AsyncClient(proxies=proxie2, timeout=20, headers=get_headers()) as client:
                url = resp.raw[0].thumbnail
                r = await client.get(url)
                img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
                path = "data/pictures/cache/" + random_str() + ".png"
                img.save(path)
        except:
            path="data/autoReply/imageReply/axaAaRaUaaafa7a.png"



    fs="标题："+str(resp.raw[0].title)+"\n"+"链接："+str(resp.raw[0].url)+"分类："+str(resp.raw[0].type)+"\n日期："+str(resp.raw[0].date)
    print(fs)
    return "Ehentai:"+fs+"\n============",path

async def saucenoS(url,api_key,proxies):
    async with Network(proxies=proxies) as client:
        saucenao = SauceNAO(client=client, api_key=api_key, hide=3)
        #resp = await saucenao.search(url=url)
        resp = await saucenao.search(file=url.replace(r"\\","/"))
        print(str(resp.raw[0].origin).replace(",","\n"))
        proxie2 = {
            "http://": proxies,
            "https://": proxies
        }
        try:
            async with httpx.AsyncClient(proxies=proxie2,timeout=20, headers=get_headers()) as client:
                url=resp.raw[0].origin.get("header").get("thumbnail")
                r = await client.get(url)
                img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
                path="data/pictures/cache/"+random_str()+".png"
                img.save(path)
        except:
            path="data/autoReply/imageReply/axaAaRaUaaafa7a.png"
        return "sauceno获取到结果：\n"+str(resp.raw[0].origin).replace(",","\n")+"\n============",path
        #show_result(resp)


'''if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())'''

def get_headers():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]

    userAgent = random.choice(user_agent_list)
    headers = {'User-Agent': userAgent}
    return headers

if __name__ == "__main__":

    asyncio.run(saucenoS(Path("C:\\Users\\DEII\\Documents\\Tencent Files\\3377428814\\nt_qq\\nt_data\\Pic\\2023-10\\Ori\\46fc710e46d18b771343903e837eff71.jpg"),"b1f018dbf8b7c21c38b4d9ad0211f8db1c4eaf20","http://127.0.0.1:1080"))

