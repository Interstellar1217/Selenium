import requests
import json


def send_to_wechat_robot(webhook_url, message):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": message
        }
    }

    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print("Message sent successfully.")
    else:
        print(f"Failed to send message: {response.status_code}")
