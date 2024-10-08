import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from config import TARGET_KEYWORD_LEFT, MAX_ITEMS_LEFT, MAX_ITEMS_RIGHT


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

            # 解析时间
            try:
                hour, minute, second = map(int, re.match(r'(\d{2}):(\d{2}):(\d{2})', time_text).groups())
                news_time = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
            except (AttributeError, ValueError):
                print(f"无法解析时间 {time_text}，跳过此条目。")
                continue

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


def parse_right_html_content(iframe_content, max_items=MAX_ITEMS_RIGHT):
    print("开始解析右侧 HTML 内容")

    soup = BeautifulSoup(iframe_content, 'html.parser')

    # 找到所有数据项
    data_items = soup.find_all('div', class_='jin-list-item is-data')
    if not data_items:
        print("未找到右侧财经日历的数据项")
        return []

    right_news = []
    for item in data_items:
        time_element = item.find('span', class_='time')
        name_element = item.find('a')  # 名称在 <a> 标签内
        affect_element = item.find('div', class_='data-affect')

        if time_element and name_element:
            time_text = time_element.text.strip()
            name_text = name_element.text.strip()

            affects = affect_element.text.strip() if affect_element else "N/A"

            # 获取前值、预期和公布
            values = {
                '前值': 'N/A',
                '预期': 'N/A',
                '公布': 'N/A'
            }

            try:
                # 查找前值
                prev_value_span = item.find('span', text=re.compile(r'前值'))
                if prev_value_span:
                    prev_value = prev_value_span.find_next_sibling('span', class_='data-value__num').get_text(
                        strip=True)
                    values['前值'] = prev_value

                # 查找预期
                expected_value_span = item.find('span', text=re.compile(r'预期'))
                if expected_value_span:
                    expected_value = expected_value_span.find_next_sibling('span', class_='data-value__num').get_text(
                        strip=True)
                    values['预期'] = expected_value

                # 查找公布
                published_value_span = item.find('span', text=re.compile(r'公布'))
                if published_value_span:
                    published_value = published_value_span.find_next_sibling('span', class_='data-value__num').get_text(
                        strip=True)
                    values['公布'] = published_value
            except (AttributeError, ValueError):
                print(f"无法找到前值、预期或公布的值，使用默认值 'N/A'。")

            news_item = {
                "time": time_text,
                "name": name_text,
                "affects": affects,
                "values": values
            }
            right_news.append(news_item)

            if len(right_news) >= max_items:
                print(f"已达到最大条数 {max_items}，停止获取。")
                break
        else:
            print("缺少时间或名称元素。")

    if not right_news:
        print("右侧 IFrame 中没有找到新闻。")

    return right_news
