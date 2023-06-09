import time

from amiyabot import Chain
from amiyabot import Message
from playwright.async_api import async_playwright

from ai.gpt.chatgpt import ChatGPT
from configs import normal_order_level, bot, PROXY_IP, PROXY_PORT, system_order
from utils.argument_parser import ArgumentParser


def get_middle_chars(s, n):
    middle = len(s) // 2
    start = middle - n // 2
    end = start + n
    return s[start:end]

def split_string(string, n):
    return [string[i:i+n] for i in range(0, len(string), n)]

class Meta:
    command = "#搜索"
    description = "通过搜索引擎搜索相关内容，并通过GPT进行资料整理。"

# 请求网站
async def search_verify(data: Message):
    return True if data.text.startswith(Meta.command) else None
@bot.on_message(verify=search_verify, level=normal_order_level, check_prefix=False)
async def search_website(data: Message):
    # 解析参数
    parser = ArgumentParser(prog=Meta.command, description=Meta.description, exit_on_error=False)

    # 添加选项和参数
    parser.add_argument('-k', '--keyword', type=str, default="kalinote.top", help="需要搜索的关键词，默认为\"kalinote.top\"")

    # 解析命令
    try:
        args = parser.do_parse(data.text)
    except Exception as info:
        # 实际上不一定是错误，-h也会触发
        return Chain(data).text(info.__str__())

    keyword = args.keyword
    url = f"https://www.google.com/search?q={keyword}"

    await bot.send_message(Chain().at(data.user_id).text("[实验功能]正在请求搜索内容，由于openai限制每分钟请求数，所以内容较多的页面可能会较慢，请稍等..."), channel_id=data.channel_id)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            proxy={
                "server": f"{PROXY_IP}:{PROXY_PORT}",
                "username": "",
                "password": ""
            }
        )
        page = await browser.new_page()
        await page.goto(url, wait_until="load")

        # 定位第一个 <h3> 标签的父标签并跳转
        # h3_element = await page.query_selector('h3')
        # parent_element = await h3_element.query_selector('xpath=..')
        # await page.goto(await parent_element.get_attribute('href'))

        # 处理机器人验证
        if await page.query_selector("#rc-anchor-container"):
            # print("执行了处理机器人验证")
            await page.click("#rc-anchor-container")


        h3_elements = await page.query_selector_all('h3')
        if not h3_elements:
            # 页面中没有h3元素
            await bot.send_message(Chain().text("出现错误，没有在google的搜索页面找到h3，请稍后或换一个关键词重试！"), channel_id=data.channel_id)
            # print(await page.content())
            screenshot_bytes = await page.screenshot(full_page=True)
            return Chain(data).image(screenshot_bytes)

        for h3_element in h3_elements:
            parent_element = await h3_element.query_selector("xpath=..")
            if not parent_element:
                continue
            href = await parent_element.get_attribute('href')
            if href is not None:
                # 找到具有href属性的父元素
                await page.goto(href)
                break


        screenshot_bytes = await page.screenshot(full_page=True)
        await bot.send_message(Chain().image(screenshot_bytes), channel_id=data.channel_id)

        # content = await page.inner_text('h1, p, div')
        full_content = await page.inner_text('body')

    content_list = split_string(full_content, 3000)
    count = 0
    for content in content_list:
        count += 1
        gpt = ChatGPT(temperature=0.3, system_order=system_order['网页分析助手'])
        await bot.send_message(Chain().text(f"第{count}/{len(content_list)}段：\n" + await gpt.call(content)), channel_id=data.channel_id)
        time.sleep(1)

    return
