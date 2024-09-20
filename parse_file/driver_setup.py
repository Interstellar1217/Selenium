import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    )

    # 指定 Chrome 和 chromedriver 路径
    chrome_binary_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    chromedriver_path = "D:/chromedriver-win64/chromedriver.exe"

    chrome_options.binary_location = chrome_binary_path
    service = Service(executable_path=chromedriver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
