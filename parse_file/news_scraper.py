import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def read_external_html(url, driver):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        iframes = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'iframe')))

        if len(iframes) > 0:
            driver.switch_to.frame(iframes[0])
            elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jin-flash_item')))

            max_items = 200
            current_items = 0

            while current_items < max_items:
                load_more_link = driver.find_elements(By.ID, 'J_flashMoreBtn')
                if not load_more_link or current_items >= max_items:
                    break
                load_more_link[0].click()
                time.sleep(2)
                elements = driver.find_elements(By.CLASS_NAME, 'jin-flash_item')
                current_items = len(elements)

            last_height = driver.execute_script("return document.body.scrollHeight")
            max_scroll_attempts = 50
            scroll_attempts = 0

            while scroll_attempts < max_scroll_attempts:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1

            iframe_content = driver.page_source
            driver.switch_to.default_content()
            return iframe_content
        else:
            print("没有找到 iframe。")
            return None
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None
