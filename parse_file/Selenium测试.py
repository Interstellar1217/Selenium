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

print(sys.prefix)
print("Current Working Directory:", os.getcwd())
print("PYTHONPATH:", os.environ.get('PYTHONPATH'))
print("Path:", os.environ.get('PATH'))


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


def read_external_html(url, driver):
    try:
        driver.get(url)

        # 等待页面中的 iframe 元素加载
        wait = WebDriverWait(driver, 10)
        iframes = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'iframe')))
        print(f"页面上找到 {len(iframes)} 个 iframe。")

        iframe_contents = []
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            try:
                # 等待 iframe 内的指定元素加载
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'jin-flash_item')))
                print("iframe 内找到 'jin-flash_item' 元素。")
                iframe_contents.append(driver.page_source)
            except Exception as e:
                print(f"未找到 'jin-flash_item' 元素: {e}")
            driver.switch_to.default_content()

        return iframe_contents
    except Exception as e:
        print(f"无法从 {url} 获取数据: {e}")
        return []


def parse_left_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    flash_items = soup.find_all('div', class_='jin-flash_item')

    if not flash_items:
        print("未找到任何 'jin-flash_item' 元素。")
        return []

    news_list = []
    for item in flash_items:
        time_element = item.find('div', class_='jin-flash_time')
        text_element = item.find('p', class_='J_flash_text')

        if time_element and text_element:
            time_text = time_element.text.strip()
            text_text = text_element.text.strip()
            news_list.append({"time": time_text, "text": text_text})
        else:
            print("某个项目缺少时间或文本元素。")

    print("解析的市场快讯：")
    print(news_list)
    return news_list


def parse_right_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    list_items = soup.find_all('div', class_='jin-list-item is-data')

    if not list_items:
        print("未找到任何 'jin-list-item is-data' 元素。")
        return []

    calendar_list = []
    for item in list_items:
        time = item.find('span', class_='time').text.strip() if item.find('span', class_='time') else ''
        title = item.find('a', href=lambda x: x and "/detail/" in x).text.strip() if item.find('a', href=lambda
            x: x and "/detail/" in x) else ''
        value = item.find('span', class_='actual').text.strip() if item.find('span', class_='actual') else ''
        calendar_list.append({"time": time, "title": title, "value": value})

    print("解析的财经日历：")
    print(calendar_list)
    return calendar_list


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
    urls = ["https://interstellar1217.github.io/Selenium/"]
    driver = setup_driver()

    try:
        for url in urls:
            print(f"从 {url} 获取数据中...")
            iframe_contents = read_external_html(url, driver)

            if len(iframe_contents) >= 2:
                # 解析左侧市场快讯
                market_news = parse_left_html_content(iframe_contents[0])
                # 解析右侧财经日历
                financial_calendar = parse_right_html_content(iframe_contents[1])

                if market_news and financial_calendar:
                    # 构造消息内容
                    news_message = "\n".join([
                        f"时间：{item['time']}\n内容：{item['text']}\n{'-' * 50}"
                        for item in market_news
                    ])

                    calendar_message = "\n".join([
                        f"时间：{item['time']}\n标题：{item['title']}\n值：{item['value']}\n{'-' * 50}"
                        for item in financial_calendar
                    ])

                    full_message = f"Market News:\n{news_message}\n\nFinancial Calendar:\n{calendar_message}"

                    # 示例Webhook URL
                    webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=df41d4fb-8327-4dce-a190-ccfd1736823c"

                    send_to_wechat_robot(webhook_url, full_message)
                else:
                    print("无可用的新闻数据或财经日历数据。")
            else:
                print("未找到足够的 iframe 内容。")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
