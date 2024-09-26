import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

            # 访问页面并获取左侧 iframe 内容
            iframe_content_left = read_external_html(url, driver, max_items=MAX_ITEMS_LEFT)

            # 切换回默认内容
            driver.switch_to.default_content()

            # 找到所有的iframe元素
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')

            # 确保找到了两个iframe
            if len(iframes) != 2:
                print("页面上的iframe数量不正确，预期为2个。")
                continue

            # 获取右侧的iframe (索引1)
            right_iframe = iframes[1]

            # 等待右侧iframe加载完成并切换到它
            wait = WebDriverWait(driver, 10)
            wait.until(EC.frame_to_be_available_and_switch_to_it(right_iframe))

            # 检查是否有嵌套的iframe
            nested_iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            if nested_iframes:
                # 如果有嵌套的iframe，切换到第一个嵌套的iframe
                driver.switch_to.frame(nested_iframes[0])

            # 获取右侧iframe的内容
            iframe_content_right = driver.page_source

            # 将内容保存到文件
            with open('right_iframe_content.html', 'w', encoding='utf-8') as f:
                f.write(iframe_content_right)

            # 切换回默认内容
            driver.switch_to.default_content()

            if iframe_content_left and iframe_content_right:
                print("成功获取 iframe 内容，开始解析...")

                # 解析左侧 iframe 内容（按关键词过滤）
                left_news = parse_left_html_content(iframe_content_left, max_items=MAX_ITEMS_LEFT)

                # 解析右侧 iframe 内容（全部获取）
                right_news = parse_right_html_content(iframe_content_right, max_items=MAX_ITEMS_RIGHT)

                # 过滤左侧新闻中包含主关键词的内容
                filtered_left_news = [news for news in left_news if "金十数据整理" in news['text']]

                # 格式化左侧新闻
                formatted_left_news = "\n\n".join([
                    f"{index + 1}. **时间**：{item['time']}\n**内容**：\n{item['text']}\n{'-' * 50}"
                    for index, item in enumerate(filtered_left_news)
                ])

                # 只取右侧新闻的前十条
                top_10_right_news = right_news[:10]

                # 格式化右侧新闻
                formatted_right_news = "\n\n".join([
                    f"{index + 1}. **时间**：{item['time']}\n**名称**：{item['name']}\n**影响**：{item['affects']}\n"
                    f"**前值**：{item['values'].get('前值', 'N/A')}\n**预期**：{item['values'].get('预期', 'N/A')}\n"
                    f"**公布**：{item['values'].get('公布', 'N/A')}\n{'-' * 50}"
                    for index, item in enumerate(top_10_right_news)
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
