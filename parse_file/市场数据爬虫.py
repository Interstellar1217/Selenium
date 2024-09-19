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
import schedule

# 打印当前 Python 环境的一些信息
print(sys.prefix)
print("Current Working Directory:", os.getcwd())
print("PYTHONPATH:", os.environ.get('PYTHONPATH'))
print("Path:", os.environ.get('PATH'))


# 设置 Chrome WebDriver
def setup_driver():
    # 创建 Chrome 选项
    chrome_options = webdriver.ChromeOptions()
    # 设置 User-Agent
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3")
    # 指定 Chrome 可执行文件路径
    chrome_binary_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    # 指定 chromedriver 路径
    chromedriver_path = "D:/chromedriver-win64/chromedriver.exe"
    # 设置 Chrome 二进制文件位置
    chrome_options.binary_location = chrome_binary_path
    # 创建服务对象
    service = Service(executable_path=chromedriver_path)
    # 创建 WebDriver 实例
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# 读取外部 HTML 内容
def read_external_html(url, driver):
    try:
        # 访问指定 URL
        driver.get(url)

        # 等待页面中的 iframe 元素加载
        wait = WebDriverWait(driver, 10)
        iframes = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'iframe')))
        print(f"页面上找到 {len(iframes)} 个 iframe。")

        # 假设左侧的 iframe 是第一个
        if len(iframes) > 0:
            driver.switch_to.frame(iframes[0])
            try:
                # 尝试找到 'jin-flash_item' 类的元素
                elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jin-flash_item')))
                print("iframe 内找到 'jin-flash_item' 元素。")

                # 设置获取的数据条数限制
                max_items = 10
                current_items = 0

                # 检查是否有“点击加载更多”链接并点击
                while current_items < max_items:
                    load_more_link = driver.find_elements(By.ID, 'J_flashMoreBtn')
                    if not load_more_link or current_items >= max_items:
                        break

                    # 点击“点击加载更多”链接
                    load_more_link[0].click()
                    time.sleep(2)  # 等待新数据加载

                    # 获取当前加载的所有数据项
                    elements = driver.find_elements(By.CLASS_NAME, 'jin-flash_item')
                    current_items = len(elements)

                # 设置滚动次数限制
                max_scroll_attempts = 50
                scroll_attempts = 0

                # 模拟滚动加载更多数据
                last_height = driver.execute_script("return document.body.scrollHeight")
                while scroll_attempts < max_scroll_attempts:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # 等待新数据加载
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                    scroll_attempts += 1

                # 获取当前页面的 HTML 内容
                iframe_content = driver.page_source
            except Exception as e:
                print(f"未找到 'jin-flash_item' 元素: {e}")
                iframe_content = None
            finally:
                # 切换回默认内容
                driver.switch_to.default_content()

            return iframe_content
        else:
            print("没有找到任何 iframe。")
            return None
    except Exception as e:
        print(f"无法从 {url} 获取数据: {e}")
        return None


# 解析新闻数据
# 解析左侧 HTML 内容
def parse_left_html_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    flash_items = soup.find_all('div', class_='jin-flash_item')

    # 打印原始 HTML 内容
    with open("raw_html.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    news_list = []
    # 关键词
    target_keyword = "金十数据整理"

    for item in flash_items:
        time_element = item.find('div', class_='jin-flash_time')
        text_element = item.find('p', class_='J_flash_text')

        # 打印每个项目的详细信息
        print(f"Item: {item.prettify()}")

        if time_element and text_element:
            time_text = time_element.text.strip()
            text_text = text_element.text.strip()

            # 查找包含关键词 "金十数据整理" 的新闻
            if target_keyword in text_text:
                news_list.append({"time": time_text, "text": text_text})
                print(f"找到包含关键词 '{target_keyword}' 的新闻，停止继续搜索。")
                break  # 找到第一条新闻后停止搜索
        else:
            print("某个 'jin-flash_item' 缺少时间或文本元素。")

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


# 定时任务函数
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
        # 关闭 WebDriver
        driver.quit()


# 主函数 - 立即运行抓取新闻
def main():
    # 立即执行抓取新闻数据的函数
    fetch_market_news()


if __name__ == "__main__":
    main()
