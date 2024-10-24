import os
import re
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_setup import setup_driver
from news_scraper import read_external_html
from html_parser import parse_left_html_content, parse_right_html_content
from wechat_bot import send_to_wechat_robot
from config import WECHAT_WEBHOOK_URL, URLS, MAX_ITEMS_LEFT, MAX_ITEMS_RIGHT, TARGET_KEYWORD_LEFT_MORNING, \
    TARGET_KEYWORD_LEFT_NIGHT

# 打印当前工作目录与当前时间
print(f"当前工作目录: {os.getcwd()}")
print(f"当前时间：{time.ctime()}")


def format_left_news(news_list):
    """
    格式化左侧新闻列表，确保每段输出信息不超过2048字节。
    如果消息长度超过2048字节，则按序号完整地删除整个条目，直到消息长度符合企业微信输出要求。
    """

    # 初始化格式化的消息和长度计数器
    formatted_message = ""
    message_length = 0
    max_message_length = 2048

    for item in news_list:
        text = item['text']
        # 使用正则表达式匹配并移除前缀及其后面的日期
        text = re.sub(r'金十数据整理：\(.*?\)', '', text)
        # 去除多余的空格和特殊字符
        text = text.strip()

        # 检查是否有小标题
        if "金十数据整理：每日全球大宗商品市场要闻速递" in text:
            for section in ["贵金属和矿业", "农产品"]:
                if section in text:
                    text = text.replace(section, f"\n\n**{section}**")

        # 按照序号逐条添加条目
        matches = re.findall(r'(\d+\.\s+.*?)(?=\d+\.\s+|$)', text, re.DOTALL)
        for match in matches:
            new_message = f"{match}\n\n"
            if message_length + len(new_message) > max_message_length:
                return formatted_message
            formatted_message += new_message
            message_length += len(new_message)

    return formatted_message


def format_right_news(news_list, max_items=30):
    news_list = news_list[:max_items]

    return "\n\n".join([
        f"{index + 1}. **名称**：{item['name']}\n"
        f"**前值**：{item['values'].get('前值', 'N/A')}\n"
        f"**预期**：{item['values'].get('预期', 'N/A')}\n"
        f"**公布**：{item['values'].get('公布', 'N/A')}\n"
        for index, item in enumerate(news_list)
    ])


def fetch_market_news():
    # 获取当前时间
    now = datetime.now()
    current_hour = now.hour

    # 根据当前时间选择合适的关键字
    if 8 <= current_hour < 16:
        target_keyword_left = TARGET_KEYWORD_LEFT_MORNING
    else:
        target_keyword_left = TARGET_KEYWORD_LEFT_NIGHT

    print(f"使用的关键词: {target_keyword_left}")

    driver = setup_driver()

    try:
        for url in URLS:
            # 访问页面并获取左侧 iframe 内容
            iframe_content_left = read_external_html(url, driver, max_items=MAX_ITEMS_LEFT)

            # 将左侧 iframe 内容保存到文件
            with open('left_iframe_content.html', 'w', encoding='utf-8') as f:
                f.write(iframe_content_left)
            print("已将左侧 iframe 内容保存到 left_iframe_content.html 文件中")

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
            print("已将右侧 iframe 内容保存到 right_iframe_content.html 文件中")

            # 切换回默认内容
            driver.switch_to.default_content()

            if iframe_content_left and iframe_content_right:
                print("成功获取 iframe 内容，开始解析...")

                # 解析左侧 iframe 内容（按关键词过滤）
                left_news = parse_left_html_content(iframe_content_left, max_items=MAX_ITEMS_LEFT)

                # 解析右侧 iframe 内容（全部获取）
                right_news = parse_right_html_content(iframe_content_right, max_items=MAX_ITEMS_RIGHT)

                # 分别处理每个关键字
                if isinstance(target_keyword_left, list):
                    formatted_left_news_segments = []
                    for keyword in target_keyword_left:
                        filtered_news = [news for news in left_news if keyword in news.get('text', '')]
                        formatted_message = format_left_news(filtered_news)
                        formatted_left_news_segments.append(formatted_message)
                else:
                    filtered_news = [news for news in left_news if target_keyword_left in news.get('text', '')]
                    formatted_left_news_segments = [format_left_news(filtered_news)]

                # 在发送消息之前打印内容
                for segment in formatted_left_news_segments:
                    print(f"左侧市场数据:\n{segment}")

                # 分别发送左侧的消息
                for segment in formatted_left_news_segments:
                    if segment:
                        left_message = "## 市场数据:\n" + segment
                        send_to_wechat_robot(WECHAT_WEBHOOK_URL, left_message)

                # 格式化右侧新闻
                formatted_right_news = format_right_news(right_news)

                # 在发送消息之前打印内容
                print(f"右侧财经日历:\n{formatted_right_news}")

                # 发送右侧的消息
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
