from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import traceback


def setup_driver():
    # 设置 Chrome WebDriver
    options = Options()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def fetch_calendar_data():
    print("开始执行 fetch_calendar_data 函数")
    driver = setup_driver()

    try:
        # 打开目标网页
        driver.get("https://rili.jin10.com/")

        # 显式等待，确保财经日历表格加载完成
        wait = WebDriverWait(driver, 60)  # 增加等待时间到 60 秒

        # 等待财经日历表格加载完成
        calendar_table_locator = (By.CLASS_NAME, 'jin-table-body__wrapper')
        try:
            calendar_table = wait.until(EC.presence_of_element_located(calendar_table_locator))
            print("财经日历表格找到了")
        except Exception as e:
            print(f"找不到财经日历表格: {e}")
            return

        # 打印当前页面的源代码
        print("页面源代码:")
        print(driver.page_source)

        # 获取所有的行
        rows = calendar_table.find_elements(By.CSS_SELECTOR, '.jin-table-row')

        for row in rows:
            try:
                # 提取时间
                time_element_css = row.find_element(By.CSS_SELECTOR, '.first-time .cell span')
                time_element_xpath = row.find_element(By.XPATH, ".//div[@class='first-time']/div/span")
                time_css = time_element_css.text.strip()
                time_xpath = time_element_xpath.text.strip()
                print(f"找到时间 (CSS): {time_css}")
                print(f"找到时间 (XPath): {time_xpath}")

                # 提取数据名称
                title_element_css = row.find_element(By.CSS_SELECTOR, '.jin-table-column:nth-child(2) .cell a')
                title_element_xpath = row.find_element(By.XPATH,
                                                       ".//div[contains(@class, 'jin-table-column')][2]/div/a")
                title_css = title_element_css.text.strip()
                title_xpath = title_element_xpath.text.strip()
                print(f"找到标题 (CSS): {title_css}")
                print(f"找到标题 (XPath): {title_xpath}")

                # 提取重要性
                importance_element_css = row.find_element(By.CSS_SELECTOR, '.jin-table-column:nth-child(3) .cell')
                importance_element_xpath = row.find_element(By.XPATH,
                                                            ".//div[contains(@class, 'jin-table-column')][3]/div")
                importance_css = importance_element_css.text.strip()
                importance_xpath = importance_element_xpath.text.strip()
                print(f"找到重要性 (CSS): {importance_css}")
                print(f"找到重要性 (XPath): {importance_xpath}")

                # 提取前值
                previous_value_element_css = row.find_element(By.CSS_SELECTOR, '.jin-table-column:nth-child(4) .cell')
                previous_value_element_xpath = row.find_element(By.XPATH,
                                                                ".//div[contains(@class, 'jin-table-column')][4]/div")
                previous_value_css = previous_value_element_css.text.strip()
                previous_value_xpath = previous_value_element_xpath.text.strip()
                print(f"找到前值 (CSS): {previous_value_css}")
                print(f"找到前值 (XPath): {previous_value_xpath}")

                # 提取预测值
                expected_value_element_css = row.find_element(By.CSS_SELECTOR, '.jin-table-column:nth-child(5) .cell')
                expected_value_element_xpath = row.find_element(By.XPATH,
                                                                ".//div[contains(@class, 'jin-table-column')][5]/div")
                expected_value_css = expected_value_element_css.text.strip()
                expected_value_xpath = expected_value_element_xpath.text.strip()
                print(f"找到预期值 (CSS): {expected_value_css}")
                print(f"找到预期值 (XPath): {expected_value_xpath}")

                # 提取公布值
                actual_value_element_css = row.find_element(By.CSS_SELECTOR, '.jin-table-column:nth-child(6) .cell')
                actual_value_element_xpath = row.find_element(By.XPATH,
                                                              ".//div[contains(@class, 'jin-table-column')][6]/div")
                actual_value_css = actual_value_element_css.text.strip()
                actual_value_xpath = actual_value_element_xpath.text.strip()
                print(f"找到公布值 (CSS): {actual_value_css}")
                print(f"找到公布值 (XPath): {actual_value_xpath}")

                # 提取影响
                affect_element_css = row.find_element(By.CSS_SELECTOR, '.jin-table-column:nth-child(7) .cell')
                affect_element_xpath = row.find_element(By.XPATH, ".//div[contains(@class, 'jin-table-column')][7]/div")
                affect_css = affect_element_css.text.strip()
                affect_xpath = affect_element_xpath.text.strip()
                print(f"找到影响 (CSS): {affect_css}")
                print(f"找到影响 (XPath): {affect_xpath}")

                # 提取解读
                interpretation_element_css = row.find_element(By.CSS_SELECTOR, '.jin-table-column:last-child .cell')
                interpretation_element_xpath = row.find_element(By.XPATH,
                                                                ".//div[contains(@class, 'jin-table-column')][last()]/div")
                interpretation_css = interpretation_element_css.text.strip()
                interpretation_xpath = interpretation_element_xpath.text.strip()
                print(f"找到解读 (CSS): {interpretation_css}")
                print(f"找到解读 (XPath): {interpretation_xpath}")

                # 打印提取的数据
                print(f"时间 (CSS): {time_css}")
                print(f"时间 (XPath): {time_xpath}")
                print(f"标题 (CSS): {title_css}")
                print(f"标题 (XPath): {title_xpath}")
                print(f"重要性 (CSS): {importance_css}")
                print(f"重要性 (XPath): {importance_xpath}")
                print(f"前值 (CSS): {previous_value_css}")
                print(f"前值 (XPath): {previous_value_xpath}")
                print(f"预期值 (CSS): {expected_value_css}")
                print(f"预期值 (XPath): {expected_value_xpath}")
                print(f"公布值 (CSS): {actual_value_css}")
                print(f"公布值 (XPath): {actual_value_xpath}")
                print(f"影响 (CSS): {affect_css}")
                print(f"影响 (XPath): {affect_xpath}")
                print(f"解读 (CSS): {interpretation_css}")
                print(f"解读 (XPath): {interpretation_xpath}")
                print("-" * 40)

            except Exception as e:
                print(f"处理行时发生错误: {e}")
                print(traceback.format_exc())  # 打印详细的错误堆栈
                continue

    finally:
        # 关闭 WebDriver
        driver.quit()


if __name__ == "__main__":
    fetch_calendar_data()
