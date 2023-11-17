import asyncio
from asyncio import sleep

import func_timeout
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


async def webScreenShoot(url,path,width=1200,height=900):
    browser = webdriver.Firefox()
    url = url
    browser.set_window_size(width,height)
    browser.get(url)
    await sleep(2)
    browser.save_screenshot(path)
    browser.close()


# !/usr/bin/python3
# -*- coding:utf-8 -*-


import time
from selenium import webdriver

from PIL import Image


async def screenshot_to_pdf_and_png(link,path,waitT=1):
    ''' 参数：网址
        功能: 保存网址截图
             解决了截图不全问题
             解决了懒加载问题
             保存俩种图片格式
    '''



    driver = webdriver.Firefox()
    # 6> 模仿手动滑动滚动条，解决懒加载问题
    try:
        driver.implicitly_wait(1)
        driver.get(link)

        # 模拟人滚动滚动条,处理图片懒加载问题
        js_height = "return document.body.clientHeight"
        driver.get(link)
        k = 1
        height = driver.execute_script(js_height)
        while True:
            if k * 500 < height:
                js_move = "window.scrollTo(0,{})".format(k * 500)
                #print(js_move)
                driver.execute_script(js_move)
                await sleep(0.2)

                height = driver.execute_script(js_height)
                k += 1
            else:
                break

        await sleep(1) ##app > div.content > div > div > div.bili-dyn-item__main
        #document.querySelector("#app > div.content > div > div > div.bili-dyn-item__main")
        #/html/body/div[2]/div[3]/div/div/div[1]
        # 7>  # 直接截图截不全，调取最大网页截图
        width = driver.execute_script(
            "return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
        height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
        #print(width, height)
        # 将浏览器的宽高设置成刚刚获取的宽高
        driver.set_window_size(width + 100, height + 100)
        await sleep(waitT)
        png_path = path

        # 截图并关掉浏览器
        driver.save_screenshot(png_path)
        driver.close()
        # png转pdf
        #image1 = Image.open(png_path)
        #im1 = image1.convert('RGB')
        #pdf_path = png_path.replace('.png', '.pdf')
        #im1.save(pdf_path)
        return png_path

    except Exception as e:
        print(e)

def BiliDynamicsScreen(lat,path):
    url = "https://t.bilibili.com/" + str(lat)
    # 导入selenium库

    options = Options()
    # 禁止弹出通知
    options.add_argument("--disable-notifications")
    # 禁止弹出其他类型的悬浮窗

    # 创建一个Chrome浏览器对象
    driver = webdriver.Firefox(options)

    # 打开一个网页
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2)")
    # 定位目标元素，这里以#app > div.content > div > div > div.bili-dyn-item__main为例
    element = driver.find_element(by=By.CSS_SELECTOR, value='#app > div.content > div > div > div.bili-dyn-item__main')
    time.sleep(2)
    # 对目标元素进行截图，并保存为png文件
    element.screenshot(path)

    # 关闭浏览器
    driver.quit()
    return path,lat


if __name__ == '__main__':
    #asyncio.run(screenshot_to_pdf_and_png("https://t.bilibili.com/852273854020583459","./test.png"))
    asyncio.run(biliScreen("https://t.bilibili.com/852273854020583459","test.png"))

