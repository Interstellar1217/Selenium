import re
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from config import TARGET_KEYWORD_LEFT, MAX_ITEMS_LEFT, MAX_ITEMS_RIGHT


# 解析左侧 HTML 内容 (根据关键字)
def parse_left_html_content(html_content, max_items=MAX_ITEMS_LEFT):
    print("开始解析左侧 HTML 内容")
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
                    print("新闻时间早于24小时前，跳过。")
                    continue

                if TARGET_KEYWORD_LEFT in text_text:
                    news_list.append({"time": time_text, "text": text_text})
                    print(f"找到包含关键词 '{TARGET_KEYWORD_LEFT}' 的新闻。")

                    # 只获取前 max_items 条新闻
                    if len(news_list) >= max_items:
                        print(f"已达到最大条数 {max_items}，停止搜索。")
                        break
        else:
            print("某个 'jin-flash_item' 缺少时间或文本元素。")

    if not news_list:
        print(f"没有找到包含关键词 '{TARGET_KEYWORD_LEFT}' 的新闻。")

    return news_list


# 解析右侧 HTML 内容 (全部获取)
def parse_right_html_content(html_content, max_items=MAX_ITEMS_RIGHT):
    print("开始解析右侧 HTML 内容")
    soup = BeautifulSoup(html_content, 'html.parser')
    list_items = soup.find_all('div', class_='jin-list-item is-data')

    right_list = []
    for item in list_items:
        time_element = item.find('span', class_='time')
        name_element = item.find('div', class_='data-name')
        affect_element = item.find('div', class_='affect2')
        value_elements = item.find_all('div', class_='data-value')

        if time_element and name_element:
            time_text = time_element.text.strip()
            name_text = name_element.text.strip()

            affects = affect_element.text.strip() if affect_element else "N/A"
            values = {}
            for v in value_elements:
                title = v.find('span', class_='data-value__title').text.strip()
                num = v.find('span', class_='data-value__num').text.strip()
                values[title] = num

            print(f"找到右侧新闻 - 时间: {time_text}, 名称: {name_text}")

            news_item = {
                "time": time_text,
                "name": name_text,
                "affects": affects,
                "values": values
            }
            right_list.append(news_item)

            if len(right_list) >= max_items:
                print(f"已达到最大条数 {max_items}，停止获取。")
                break
        else:
            print("缺少时间或名称元素。")

    if not right_list:
        print("右侧 IFrame 中没有找到新闻。")

    return right_list
