import os

# 企业微信 Webhook URL
WECHAT_WEBHOOK_URL = os.environ.get('WECHAT_WEBHOOK_URL', 'WECHAT_WEBHOOK_URL')

# 其他配置
TARGET_KEYWORD_LEFT = "金十数据整理：每日期货市场要闻速递"
TARGET_KEYWORD_RIGHT = "金十数据整理"
TARGET_KEYWORD_MAIN = "金十数据整理"
MAX_ITEMS_LEFT = 500
MAX_ITEMS_RIGHT = 500
MAX_SCROLL_ATTEMPTS = 100
URLS = ["https://interstellar1217.github.io/Selenium/"]
