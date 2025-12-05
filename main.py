import requests
import os
import time

# 配置区域
TARGET_RATE = 5.35  # 你的心理价位
TOKEN = os.environ.get("PUSHPLUS_TOKEN")

def get_rate():
    # 使用免费API获取 SGD -> CNY 汇率
    url = "https://api.exchangerate-api.com/v4/latest/SGD"
    try:
        resp = requests.get(url)
        data = resp.json()
        return data['rates']['CNY']
    except:
        return None

def send_wechat(rate):
    if not TOKEN:
        print("无Token，跳过推送")
        return

    # 根据时间判断是早中晚哪个时间段
    hour = time.localtime().tm_hour + 8 # GitHub时区是UTC，加8变成新加坡/北京时间
    if hour >= 24: hour -= 24
    
    time_label = "早安"
    if 11 <= hour < 14: time_label = "午间"
    elif 17 <= hour < 20: time_label = "晚间"

    # 判断是否值得买
    advice = "📈 汇率较高，建议观望"
    color = "#FF0000" # 红色
    if rate <= TARGET_RATE:
        advice = "💰 汇率不错！可以分批购汇了！"
        color = "#008000" # 绿色

    title = f"{time_label}汇率播报：{rate}"
    content = (
        f"当前时间：{time.strftime('%H:%M')}\n"
        f"1 新币 = {rate} 人民币\n\n"
        f"{advice}\n"
        f"（你的心理价位是：{TARGET_RATE}）"
    )

    url = "http://www.pushplus.plus/send"
    data = {
        "token": TOKEN,
        "title": title,
        "content": content,
        "template": "html"
    }
    requests.post(url, json=data)
    print("推送成功")

if __name__ == "__main__":
    rate = get_rate()
    if rate:
        send_wechat(rate)
