import os
from driver_setup import setup_driver
from news_scraper import read_external_html
from html_parser import parse_left_html_content
from wechat_bot import send_to_wechat_robot

# 企业微信 Webhook URL
webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=df41d4fb-8327-4dce-a190-ccfd1736823c"


# 主函数
def fetch_market_news():
    urls = ["https://interstellar1217.github.io/Selenium/"]
    driver = setup_driver()

    try:
        for url in urls:
            print(f"从 {url} 获取数据中...")
            iframe_content = read_external_html(url, driver)

            if iframe_content:
                # 解析 HTML 内容，只获取前 10 条新闻
                market_news = parse_left_html_content(iframe_content, max_items=10)
                if market_news:
                    # 使用 Markdown 格式美化输出
                    news_message = "\n".join([
                        f"{index + 1}. **时间**：{item['time']}\n**内容**：\n{item['text']}\n{'-' * 50}"
                        for index, item in enumerate(market_news)
                    ])

                    full_message = f"## Market News:\n{news_message}"

                    # 发送到企业微信
                    print(f"准备发送消息到企业微信，消息内容：\n{full_message}")
                    send_to_wechat_robot(webhook_url, full_message)
                else:
                    print("没有符合条件的新闻。")
            else:
                print("没有找到 iframe 的内容。")
    finally:
        driver.quit()


if __name__ == "__main__":
    fetch_market_news()
