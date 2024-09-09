import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import json
import sys

print(sys.prefix)
print("Current Working Directory:", os.getcwd())
print("PYTHONPATH:", os.environ.get('PYTHONPATH'))
print("Path:", os.environ.get('PATH'))


def setup_driver():
    # 设置 WebDriver
    chrome_options = webdriver.ChromeOptions()
    # 如果需要无头模式，取消注释以下行
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')

    # 设置 User-Agent
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3")

    # 指定 Chrome和ChromeDriver的路径
    chrome_binary_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # 替换为实际的Chrome路径
    chromedriver_path = "D:/chromedriver-win64/chromedriver.exe"  # 替换为实际的ChromeDriver路径

    chrome_options.binary_location = chrome_binary_path
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def read_external_html(url, driver):
    try:
        driver.get(url)
        # 等待页面加载完成
        time.sleep(3)  # 等待一段时间让页面加载

        # 等待特定元素加载完成
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'jin-flash-item')))

        return driver.page_source
    except Exception as e:
        print(f"Failed to fetch data from {url}: {e}")
        return None


def parse_html_content(html_content):
    # 使用 BeautifulSoup 解析页面内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 假设市场快讯数据包含在特定的 HTML 元素中
    flash_items = soup.find_all('div', class_='jin-flash-item')
    news_list = []
    for item in flash_items:
        time = item.find('div', class_='item-time').text.strip() if item.find('div', class_='item-time') else ''
        title = item.find('b', class_='right-common-title').text.strip() if item.find('b',
                                                                                      class_='right-common-title') else ''
        content = item.find('div', class_='flash-text').text.strip() if item.find('div', class_='flash-text') else ''
        news_list.append({"time": time, "title": title, "content": content})

    return news_list


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


def main():
    # 获取当前文件所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 定义外部数据源 URL
    urls = [
        "https://www.jin10.com/example/jin10.com.html",
        "https://rili-d.jin10.com/open.php"
    ]

    # 设置 WebDriver
    driver = setup_driver()

    try:
        for url in urls:
            print(f"Fetching data from {url}...")
            html_content = read_external_html(url, driver)
            if html_content:
                news = parse_html_content(html_content)
                print(news)

                # 构造消息内容
                message = "\n".join([
                    f"时间：{item['time']}\n标题：{item['title']}\n内容：{item['content']}\n{'-' * 50}"
                    for item in news
                ])

                # 示例Webhook URL
                webhook_url = ("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=df41d4fb-8327-4dce-a190"
                               "-ccfd1736823c")

                send_to_wechat_robot(webhook_url, message)
            else:
                print("No news data available.")
    finally:
        # 关闭 WebDriver
        driver.quit()


if __name__ == "__main__":
    main()
