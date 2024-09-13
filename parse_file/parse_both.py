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
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    chrome_binary_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    chromedriver_path = "D:/chromedriver-win64/chromedriver.exe"
    chrome_options.binary_location = chrome_binary_path
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def read_external_html(url, driver):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    # 等待iframe元素出现
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
    time.sleep(3)  # 等待一段时间让页面加载
    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
    iframe_contents = []
    for iframe in iframes:
        driver.switch_to.frame(iframe)
        iframe_contents.append(driver.page_source)
        driver.switch_to.default_content()
    return iframe_contents


def parse_left_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    flash_items = soup.find_all('div', class_='jin-flash-item')
    news_list = []
    for item in flash_items:
        time = item.find('div', class_='item-time').text.strip() if item.find('div', class_='item-time') else ''
        title = item.find('b', class_='right-common-title').text.strip() if item.find('b',
                                                                                      class_='right-common-title') else ''
        content = item.find('div', class_='flash-text').text.strip() if item.find('div', class_='flash-text') else ''
        news_list.append({"time": time, "title": title, "content": content})
    return news_list


def parse_right_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    list_items = soup.find_all('div', class_='jin-list-item is-data')
    calendar_list = []
    for item in list_items:
        time = item.find('span', class_='time').text.strip() if item.find('span', class_='time') else ''
        title = item.find('a', href=lambda x: x and "/detail/" in x).text.strip() if item.find('a', href=lambda
            x: x and "/detail/" in x) else ''
        value = item.find('span', class_='actual').text.strip() if item.find('span', class_='actual') else ''
        calendar_list.append({"time": time, "title": title, "value": value})
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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    urls = ["https://interstellar1217.github.io/Selenium/"]
    driver = setup_driver()
    try:
        for url in urls:
            print(f"Fetching data from {url}...")
            iframe_contents = read_external_html(url, driver)

            if len(iframe_contents) > 1:
                market_news = parse_left_html_content(iframe_contents[0])
                financial_calendar = parse_right_html_content(iframe_contents[1])

                print("Market News:")
                print(market_news)
                print("Financial Calendar:")
                print(financial_calendar)

                news_message = "\n".join([
                    f"时间：{item['time']}\n标题：{item['title']}\n内容：{item['content']}\n{'-' * 50}"
                    for item in market_news
                ])

                calendar_message = "\n".join([
                    f"时间：{item['time']}\n标题：{item['title']}\n值：{item['value']}\n{'-' * 50}"
                    for item in financial_calendar
                ])

                full_message = f"Market News:\n{news_message}\n\nFinancial Calendar:\n{calendar_message}"

                webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=df41d4fb-8327-4dce-a190-ccfd1736823c"
                send_to_wechat_robot(webhook_url, full_message)
            else:
                print("No news or calendar data available.")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
