import os
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_setup import setup_driver
from news_scraper import read_external_html
from html_parser import parse_left_html_content, parse_right_html_content
from wechat_bot import send_to_wechat_robot
from config import WECHAT_WEBHOOK_URL, URLS, MAX_ITEMS_LEFT, MAX_ITEMS_RIGHT, TARGET_KEYWORD_MAIN

# 打印当前工作目录与当前时间
print(f"当前工作目录: {os.getcwd()}")
print(f"当前时间：{time.ctime()}")


def format_left_news(news_list):
    # 移除“【金十数据整理：每日期货市场要闻速递（日期】”这个文本信息
    cleaned_news_list = []
    for item in news_list:
        text = item['text']
        # 使用正则表达式匹配并移除前缀
        text = re.sub(r'【金十数据整理：每日期货市场要闻速递\(\d{1,2}月\d{1,2}日】', '', text)
        cleaned_news_list.append({'text': text})

    # 使用正则表达式提取内部的数字序号和内容
    formatted_message = ""
    for index, item in enumerate(cleaned_news_list, start=1):
        # 提取内部的数字序号和内容
        matches = re.findall(r'(\d+\.\s+.*?)(?=\d+\.\s+|$)', item['text'], re.DOTALL)
        for match in matches:
            formatted_message += f"{match.strip()}\n\n"

    return formatted_message


def format_right_news(news_list):
    return "\n\n".join([
        f"{index + 1}. **名称**：{item['name']}\n"
        f"**前值**：{item['values'].get('前值', 'N/A')}\n"
        f"**公布**：{item['values'].get('公布', 'N/A')}\n"
        for index, item in enumerate(news_list)
    ])


def fetch_market_news():
    driver = setup_driver()

    try:
        for url in URLS:
            # 访问页面并获取左侧 iframe 内容
            iframe_content_left = read_external_html(url, driver, max_items=MAX_ITEMS_LEFT)

            # 切换回默认内容
            driver.switch_to.default_content()

            # 找到所有的iframe元素
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')

            # 确保找到了两个iframe
            if len(iframes) != 2:
                print("页面上的iframe数量不正确，预期为2个。")
                continue

            # 获取右侧的iframe (索引1)
            right_iframe = iframes[1]

            # 等待右侧iframe加载完成并切换到它
            wait = WebDriverWait(driver, 10)
            wait.until(EC.frame_to_be_available_and_switch_to_it(right_iframe))

            # 检查是否有嵌套的iframe
            nested_iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            if nested_iframes:
                # 如果有嵌套的iframe，切换到第一个嵌套的iframe
                driver.switch_to.frame(nested_iframes[0])

            # 获取右侧iframe的内容
            iframe_content_right = driver.page_source

            # 将内容保存到文件（仅用于调试）
            with open('right_iframe_content.html', 'w', encoding='utf-8') as f:
                f.write(iframe_content_right)
            print("已将 iframe 内容保存到 right_iframe_content.html 文件中")

            # 切换回默认内容
            driver.switch_to.default_content()

            if iframe_content_left and iframe_content_right:
                print("成功获取 iframe 内容，开始解析...")

                # 解析左侧 iframe 内容（按关键词过滤）
                left_news = parse_left_html_content(iframe_content_left, max_items=MAX_ITEMS_LEFT)

                # 解析右侧 iframe 内容（全部获取）
                right_news = parse_right_html_content(iframe_content_right, max_items=MAX_ITEMS_RIGHT)

                # 过滤左侧市场数据中包含关键词的内容
                filtered_left_news = [news for news in left_news if TARGET_KEYWORD_MAIN in news.get('text', '')]

                # 格式化左侧市场数据
                formatted_left_news = format_left_news(filtered_left_news)

                # 过滤右侧财经日历中公布值为“未公布”的条目
                filtered_right_news = [news for news in right_news if news['values'].get('公布', 'N/A') != '未公布']

                # 格式化右侧新闻
                formatted_right_news = format_right_news(filtered_right_news)

                # 分别发送左侧和右侧的消息
                if formatted_left_news:
                    left_message = "## 市场数据:\n" + formatted_left_news
                    send_to_wechat_robot(WECHAT_WEBHOOK_URL, left_message)

                if formatted_right_news:
                    right_message = "## 财经日历:\n" + formatted_right_news
                    send_to_wechat_robot(WECHAT_WEBHOOK_URL, right_message)
            else:
                print("没有找到 iframe 的内容。")
    finally:
        print("关闭 WebDriver")
        driver.quit()


if __name__ == "__main__":
    fetch_market_news()
