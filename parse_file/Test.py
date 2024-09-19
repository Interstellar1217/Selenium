import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import json
import sys
from datetime import datetime, timedelta

# 打印当前 Python 环境信息
print(sys.prefix)
print("Current Working Directory:", os.getcwd())
print("PYTHONPATH:", os.environ.get('PYTHONPATH'))
print("Path:", os.environ.get('PATH'))


# 设置 Chrome WebDriver
def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3")
    chrome_binary_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    chromedriver_path = "D:/chromedriver-win64/chromedriver.exe"
    chrome_options.binary_location = chrome_binary_path
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# 读取 HTML 内容并处理 iframe 和滚动加载更多数据
def read_external_html(url, driver):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        iframes = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'iframe')))
        print(f"页面上找到 {len(iframes)} 个 iframe。")

        if len(iframes) > 0:
            driver.switch_to.frame(iframes[0])
            try:
                elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jin-flash_item')))
                print("iframe 内找到 'jin-flash_item' 元素。")

                # 模拟滚动和点击“加载更多”
                max_scroll_attempts = 50
                scroll_attempts = 0
                last_height = driver.execute_script("return document.body.scrollHeight")

                while scroll_attempts < max_scroll_attempts:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(60)
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                    scroll_attempts += 1

                iframe_content = driver.page_source
            finally:
                driver.switch_to.default_content()

            return iframe_content
        else:
            print("没有找到任何 iframe。")
            return None
    except Exception as e:
        print(f"无法从 {url} 获取数据: {e}")
        return None


# 解析并查找符合条件的新闻
def parse_left_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    flash_items = soup.find_all('div', class_='jin-flash_item')
    news_list = []

    # 设置时间范围：从前一天0:00到现在
    current_time = datetime.now()
    previous_day = current_time - timedelta(days=1)
    start_time = previous_day.replace(hour=0, minute=0, second=0)

    # 查找关键词
    target_keyword = "金十数据整理"

    for item in flash_items:
        time_element = item.find('div', class_='jin-flash_time')
        text_element = item.find('p', class_='J_flash_text')

        if time_element and text_element:
            time_text = time_element.text.strip()
            text_text = text_element.text.strip()

            # 解析新闻的时间并检查是否在指定范围内
            news_time_str = item.get('data-id')
            if news_time_str:
                news_time = datetime.strptime(news_time_str, '%Y-%m-%d %H:%M:%S')

                if news_time >= start_time:
                    # 查找包含关键词的新闻
                    if target_keyword in text_text:
                        news_list.append({"time": time_text, "text": text_text})
                        print(f"找到包含关键词 '{target_keyword}' 的新闻。")
                        break  # 找到第一条新闻后停止搜索
                else:
                    print(f"新闻时间 {news_time} 超出指定时间范围。")

    if not news_list:
        print(f"没有找到包含关键词 '{target_keyword}' 的新闻。")

    return news_list


# 发送消息到企业微信机器人
def send_to_wechat_robot(webhook_url, message):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": message
        }
    }
    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print("Message sent successfully.")
    else:
        print(f"Failed to send message: {response.status_code}")


# 抓取市场新闻并发送到企业微信
def fetch_market_news():
    urls = ["https://interstellar1217.github.io/Selenium/"]
    driver = setup_driver()

    try:
        for url in urls:
            print(f"从 {url} 获取数据中...")
            iframe_content = read_external_html(url, driver)

            if iframe_content:
                market_news = parse_left_html_content(iframe_content)

                print("Market News:")
                print(market_news)

                if market_news:
                    news_message = "\n".join([
                        f"时间：{item['time']}\n内容：{item['text']}\n{'-' * 50}"
                        for item in market_news
                    ])

                    full_message = f"Market News:\n{news_message}"

                    # 发送到企业微信
                    webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=df41d4fb-8327-4dce-a190-ccfd1736823c"
                    send_to_wechat_robot(webhook_url, full_message)
                else:
                    print("无符合条件的新闻数据。")
            else:
                print("未找到左侧 iframe 的内容。")
    finally:
        driver.quit()


# 主函数 - 立即运行抓取新闻
def main():
    fetch_market_news()


if __name__ == "__main__":
    main()
