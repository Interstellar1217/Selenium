import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import MAX_SCROLL_ATTEMPTS, MAX_ITEMS_LEFT, MAX_ITEMS_RIGHT


def read_external_html(url, driver, max_items=200):
    try:
        print(f"访问 URL: {url}")
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        iframes = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'iframe')))
        print(f"页面上找到 {len(iframes)} 个 iframe。")

        if len(iframes) > 0:
            driver.switch_to.frame(iframes[0])
            print("切换到第一个 iframe。")

            # 点击“加载更多”按钮
            current_items = 0
            while current_items < max_items:
                load_more_link = driver.find_elements(By.ID, 'J_flashMoreBtn')
                if not load_more_link or current_items >= max_items:
                    print("没有找到“加载更多”按钮或已达到最大条数。")
                    break
                load_more_link[0].click()
                print("点击“加载更多”按钮。")
                time.sleep(2)  # 等待新数据加载
                elements = driver.find_elements(By.CLASS_NAME, 'jin-flash_item')
                current_items = len(elements)
                print(f"当前获取到 {current_items} 条数据。")

            # 滚动页面以加载更多内容
            last_height = driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            while scroll_attempts < MAX_SCROLL_ATTEMPTS:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                print(f"执行滚动操作，尝试次数: {scroll_attempts + 1}")
                time.sleep(2)  # 等待新数据加载
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("页面高度未变化，停止滚动。")
                    break
                last_height = new_height
                scroll_attempts += 1

            iframe_content = driver.page_source
            driver.switch_to.default_content()
            print("获取 iframe 内容成功，切换回默认内容。")
            return iframe_content
        else:
            print("没有找到任何 iframe。")
            return None
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None
