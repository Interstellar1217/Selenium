import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException

# 打印当前工作目录与当前时间
print(f"当前工作目录: {os.getcwd()}")
print(f"当前时间：{time.ctime()}")


def get_yesterday_date():
    from datetime import datetime, timedelta
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    return yesterday.strftime('%d')  # 只返回日期部分


def scroll_into_view(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)


def click_with_js(driver, element):
    driver.execute_script("arguments[0].click();", element)


def test_date_switch():
    # 设置WebDriver（这里以Chrome为例）
    driver = webdriver.Chrome()

    try:
        url = "https://interstellar1217.github.io/Selenium/"
        print(f"访问 URL: {url}")
        driver.get(url)

        # 等待页面加载
        wait = WebDriverWait(driver, 10)

        # 找到所有的iframe元素
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        print(f"页面上找到 {len(iframes)} 个 iframe。")

        # 确保找到了两个iframe
        if len(iframes) != 2:
            print("页面上的iframe数量不正确，预期为2个。")
            return

        # 获取右侧的iframe (索引1)
        right_iframe = iframes[1]

        # 等待右侧iframe加载完成并切换到它
        wait.until(EC.frame_to_be_available_and_switch_to_it(right_iframe))

        # 检查是否有嵌套的iframe
        nested_iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        if nested_iframes:
            # 如果有嵌套的iframe，切换到第一个嵌套的iframe
            driver.switch_to.frame(nested_iframes[0])
        else:
            print("没有找到嵌套的iframe。")
            return

        # 输出嵌套iframe中的页面内容
        print("嵌套iframe中的页面内容：")
        print(driver.page_source[:500])  # 打印前500个字符

        # 查找所有包含经济数据的div元素
        try:
            # 假设数据在一个带有特定类名的div中
            data_items = wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, "//div[contains(@class, 'jin-list-item') and contains(@class, 'is-data')]")))
            print(f"找到 {len(data_items)} 个经济数据条目。")

            for item in data_items:
                # 提取时间和名称
                time_element = item.find_element(By.XPATH, ".//span[@class='time']")
                name_element = item.find_element(By.XPATH, ".//ua")
                time_value = time_element.text.strip()
                name_value = name_element.text.strip()

                # 提取前值、预期和公布值
                previous_value = item.find_element(By.XPATH,
                                                   ".//span[text()='前值']/following-sibling::span").text.strip()
                expected_value = item.find_element(By.XPATH,
                                                   ".//span[text()='预期']/following-sibling::span").text.strip()
                actual_value = item.find_element(By.XPATH,
                                                 ".//span[text()='公布']/following-sibling::span").text.strip()

                # 打印提取的数据
                print(
                    f"时间: {time_value}, 名称: {name_value}, 前值: {previous_value}, 预期: {expected_value}, 公布: {actual_value}")

        except (NoSuchElementException, TimeoutException, ElementNotInteractableException) as e:
            print(f"无法找到经济数据条目: {e}")
            return

    finally:
        print("关闭 WebDriver")
        driver.quit()


if __name__ == "__main__":
    test_date_switch()
