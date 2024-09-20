from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from config import TARGET_KEYWORD


# 解析左侧 HTML 内容
def parse_left_html_content(html_content, max_items=10):
    print("开始解析 HTML 内容")
    soup = BeautifulSoup(html_content, 'html.parser')
    flash_items = soup.find_all('div', class_='jin-flash_item')

    news_list = []
    now = datetime.now()
    twenty_four_hours_ago = now - timedelta(hours=24)

    for item in flash_items:
        time_element = item.find('div', class_='jin-flash_time')
        text_element = item.find('p', class_='J_flash_text')

        if time_element and text_element:
            time_text = time_element.text.strip()
            text_text = text_element.text.strip()

            print(f"找到新闻 - 时间: {time_text}, 内容: {text_text}")

            # 解析时间
            time_match = re.match(r'(\d{2}):(\d{2}):(\d{2})', time_text)
            if time_match:
                hour, minute, second = map(int, time_match.groups())
                news_time = now.replace(hour=hour, minute=minute, second=second, microsecond=0)

                # 如果新闻时间早于24小时前，则跳过
                if news_time < twenty_four_hours_ago:
                    continue

                if TARGET_KEYWORD in text_text:
                    news_list.append({"time": time_text, "text": text_text})
                    print(f"找到包含关键词 '{TARGET_KEYWORD}' 的新闻。")

                    # 只获取前 max_items 条新闻
                    if len(news_list) >= max_items:
                        break
        else:
            print("某个 'jin-flash_item' 缺少时间或文本元素。")

    if not news_list:
        print(f"没有找到包含关键词 '{TARGET_KEYWORD}' 的新闻。")

    return news_list
