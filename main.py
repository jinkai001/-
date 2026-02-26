import requests
import os
import time
from bs4 import BeautifulSoup

# 配置区域
TARGET_RATE = 5.40  # 你的心理价位
TOKEN = os.environ.get("PUSHPLUS_TOKEN")

def get_boc_rate():
    try:
        # 中行外汇牌价网页
        url = "https://www.boc.cn/sourcedb/whpj/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8' # 处理中文乱码
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 找到所有表格行
        rows = soup.find_all('tr')
        
        for row in rows:
            # 找到包含"新加坡元"的那一行
            if "新加坡元" in row.text:
                cols = row.find_all('td')
                # 中行表格第4列是"现汇卖出价" (Selling Rate)，这就是我们要付的钱
                # 网页上的单位是100新币，所以要除以100
                selling_rate = float(cols[3].text) / 100
                return selling_rate
        return None
    except Exception as e:
        print(f"爬取失败: {e}")
        return None

def send_wechat(rate):
    if not TOKEN:
        print("无Token，跳过推送")
        return

    # 调整时区 (UTC+8)
    hour = time.localtime().tm_hour + 8 
    if hour >= 24: hour -= 24
    
    time_label = "早安"
    if 11 <= hour < 14: time_label = "午间"
    elif 17 <= hour < 20: time_label = "晚间"

    # 判断建议
    advice = "📈 汇率较高，建议观望"
    if rate <= TARGET_RATE:
        advice = "💰 汇率不错！中行现汇价已达标，建议购汇！"

    title = f"{time_label}中行真汇率：{rate}"
    content = (
        f"当前时间：{time.strftime('%H:%M')}\n"
        f"1 新币 = {rate} 人民币 (中行现汇卖出价)\n\n"
        f"{advice}\n"
        f"（提醒阈值：{TARGET_RATE}）"
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
    # 这里改成了调用新的爬虫函数
    rate = get_boc_rate()
    if rate:
        print(f"获取到中行汇率: {rate}")
        send_wechat(rate)
    else:
        print("获取汇率失败")
