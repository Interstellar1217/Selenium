import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 指定 Chrome 和 chromedriver 路径
CHROME_BINARY_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"
CUSTOM_CHROMEDRIVER_PATH = "D:/chromedriver-win64"


def setup_driver():
    # 设置 Chrome 选项
    chrome_options = Options()

    # 指定 User-Agent
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    )

    # 无头模式
    chrome_options.add_argument('--headless')
    # 禁用 GPU
    chrome_options.add_argument('--disable-gpu')
    # 沙盒模式
    chrome_options.add_argument('--no-sandbox')
    # 禁用 /dev/shm 共享内存
    chrome_options.add_argument('--disable-dev-shm-usage')

    # 设置 Chrome 二进制文件路径
    chrome_options.binary_location = CHROME_BINARY_PATH

    # 使用 webdriver_manager 自动管理 chromedriver，并指定下载路径
    # 设置环境变量 WDM_LOCAL 来指定下载位置
    os.environ['WDM_LOCAL'] = CUSTOM_CHROMEDRIVER_PATH
    chromedriver_path = ChromeDriverManager().install()

    # 创建 WebDriver 实例
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# 测试驱动程序设置
if __name__ == "__main__":
    driver = setup_driver()
    # 你可以在这里添加一些测试代码来验证驱动是否工作正常
    # 例如：driver.get('https://www.example.com')
    # 记得在测试完成后关闭浏览器
    driver.quit()
