import requests


def send_alert(message: str):
    url = "https://ntfy.sh/toastybt_server_7f4c91a2e8"
    requests.post(url, data=message.encode("utf-8"), timeout=10)