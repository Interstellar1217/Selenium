import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
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
                # 尝试找到 'jin-flash_item' 或 'jin-table-column' 类的元素
                elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jin-flash_item')))
                print("iframe 内找到 'jin-flash_item' 元素。")
                iframe_contents.append(driver.page_source)
            except Exception as e:
                try:
                    elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jin-table-column')))
                    print("iframe 内找到 'jin-table-column' 元素。")
                    iframe_contents.append(driver.page_source)
                except Exception as ee:
                    print(f"未找到 'jin-flash_item' 或 'jin-table-column' 元素: {ee}")
            driver.switch_to.default_content()

        for content in iframe_contents:
            print(content[:100])  # 打印前100个字符作为示例

        return iframe_contents
    except Exception as e:
        print(f"无法从 {url} 获取数据: {e}")
        return []


def parse_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    flash_items = soup.find_all('div', class_='jin-flash_item')
    table_columns = soup.find_all('div', class_='jin-table-column')

    if not flash_items and not table_columns:
        print("未找到任何 'jin-flash_item' 或 'jin-table-column' 元素。")
        return []

    news_list = []
    for item in flash_items + table_columns:
        if 'jin-flash_item' in item.get('class', []):
            time_element = item.find('div', class_='jin-flash_time')
            text_element = item.find('p', class_='J_flash_text')
            if time_element and text_element:
                time_text = time_element.text.strip()
                text_text = text_element.text.strip()
                news_list.append({"time": time_text, "text": text_text})
            else:
                print("某个 'jin-flash_item' 缺少时间或文本元素。")
        elif 'jin-table-column' in item.get('class', []):
            name_element = item.find('span', class_='data-name-text')
            if name_element:
                text = name_element.text.strip()
                news_list.append({"text": text})
            else:
                print("某个 'jin-table-column' 缺少 'data-name-text' 元素。")

    print("解析的新闻项：")
    print(news_list)
    return news_list


def main():
    urls = ["https://interstellar1217.github.io/Selenium/"]
    driver = setup_driver()

    try:
        for url in urls:
            print(f"从 {url} 获取数据中...")
            iframe_contents = read_external_html(url, driver)

            if iframe_contents:
                news = parse_html_content(iframe_contents[0])
                if news:
                    # 如果成功解析新闻，则输出
                    print(json.dumps(news, indent=4, ensure_ascii=False))
                else:
                    print("无可用的新闻数据。")
            else:
                print("未找到任何新闻内容。")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
