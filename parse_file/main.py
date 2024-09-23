import os
from driver_setup import setup_driver
from news_scraper import read_external_html
from html_parser import parse_left_html_content, parse_right_html_content
from wechat_bot import send_to_wechat_robot
from config import WECHAT_WEBHOOK_URL, URLS, TARGET_KEYWORD_MAIN, MAX_ITEMS_LEFT, MAX_ITEMS_RIGHT


def fetch_market_news():
    print("开始执行 fetch_market_news 函数")
    driver = setup_driver()

    try:
        for url in URLS:
            print(f"从 {url} 获取数据中...")
            iframe_content = read_external_html(url, driver, max_items=200)

            if iframe_content:
                print("成功获取 iframe 内容，开始解析...")
                # 解析左侧 iframe 内容（按关键词过滤）
                left_news = parse_left_html_content(iframe_content, max_items=MAX_ITEMS_LEFT)
                # 解析右侧 iframe 内容（全部获取）
                right_news = parse_right_html_content(iframe_content, max_items=MAX_ITEMS_RIGHT)

                # 过滤左侧新闻中包含主关键词的内容
                filtered_left_news = [news for news in left_news if TARGET_KEYWORD_MAIN in news['text']]

                # 格式化左侧新闻
                formatted_left_news = "\n\n".join([
                    f"{index + 1}. **时间**：{item['time']}\n**内容**：\n{item['text']}\n{'-' * 50}"
                    for index, item in enumerate(filtered_left_news)
                ])

                # 格式化右侧新闻
                formatted_right_news = "\n\n".join([
                    f"{index + 1}. **时间**：{item['time']}\n**名称**：{item['name']}\n**影响**：{item['affects']}\n"
                    f"**前值**：{item['values'].get('前值', 'N/A')}\n**预期**：{item['values'].get('预期', 'N/A')}\n"
                    f"**公布**：{item['values'].get('公布', 'N/A')}\n{'-' * 50}"
                    for index, item in enumerate(right_news)
                ])

                # 组合消息内容
                full_message = "## 左侧 Market News:\n" + (
                    formatted_left_news if formatted_left_news else "无符合条件的左侧新闻。") + "\n\n" + \
                               "## 右侧 Market News:\n" + (
                                   formatted_right_news if formatted_right_news else "无右侧新闻。")

                # 发送到企业微信
                print(f"准备发送消息到企业微信，消息内容：\n{full_message}")
                send_to_wechat_robot(WECHAT_WEBHOOK_URL, full_message)
            else:
                print("没有找到 iframe 的内容。")
    finally:
        print("关闭 WebDriver")
        driver.quit()


if __name__ == "__main__":
    fetch_market_news()
