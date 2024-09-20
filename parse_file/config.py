import os

# Chrome WebDriver 路径
CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', 'D:/chromedriver-win64/chromedriver.exe')
CHROME_BINARY_PATH = os.environ.get('CHROME_BINARY_PATH', 'C:/Program Files/Google/Chrome/Application/chrome.exe')

# 企业微信 Webhook URL
WECHAT_WEBHOOK_URL = os.environ.get('WECHAT_WEBHOOK_URL',
                                    'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=df41d4fb-8327-4dce-a190-ccfd1736823c')

# 其他配置
TARGET_KEYWORD = "金十数据整理"
MAX_ITEMS = 10
MAX_SCROLL_ATTEMPTS = 50
URLS = ["https://interstellar1217.github.io/Selenium/"]