import os

# 企业微信 Webhook URL
WECHAT_WEBHOOK_URL = os.environ.get('WECHAT_WEBHOOK_URL', 'WECHAT_WEBHOOK_URL')

# 其他配置
TARGET_KEYWORD_LEFT_MORNING = '金十数据整理：每日期货市场要闻速递'
TARGET_KEYWORD_LEFT_NIGHT = [
    r'金十数据整理：每日全球大宗商品市场要闻速递',
    r'金十数据整理：每日全球外汇市场要闻速递'
]

MAX_ITEMS_LEFT = 500
MAX_ITEMS_RIGHT = 500
MAX_SCROLL_ATTEMPTS = 100
URLS = ["https://interstellar1217.github.io/Selenium/"]
