import json
import requests


def send_to_wechat_robot(webhook_url, message):
    print(f"开始向企业微信发送消息，webhook URL: {webhook_url}")
    headers = {'Content-Type': 'application/json'}
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": message
        }
    }
    try:
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            print("消息发送成功。")
        else:
            print(f"消息发送失败：{response.status_code}，响应内容: {response.text}")
    except Exception as e:
        print(f"发送消息时出错: {e}")
