from selenium import webdriver
import sys

print(sys.prefix)
# 创建浏览器操作对象
path = 'chromedriver.exe'
browser = webdriver.Chrome()

# 访问网站
url = 'https://www.baidu.com'

browser.get(url)
# content = browser.page_source
# print(content)
