import requests
import os
import time
from bs4 import BeautifulSoup

# 配置区域
TARGET_RATE = 5.35  # 你的心理价位
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
```

---

### ⚠️ 第二步：修改 `schedule.yml` (关键！安装新零件)

这一步如果不做，你的程序会直接报错！因为 GitHub 的云端电脑里默认**没有** `BeautifulSoup` 这个库，你必须命令它安装。

1.  打开 `.github/workflows/schedule.yml` 文件。
2.  点击编辑。
3.  找到 `Install requests` 那一部分，把它改成下面这样（加了一行安装命令）：

```yaml
      - name: Install dependencies
        run: |
          pip install requests
          pip install beautifulsoup4
```

**为了方便，你可以直接复制下面这个完整的 `schedule.yml` 覆盖原来的：**

```yaml
name: Daily Exchange Rate Check

on:
  schedule:
    # 这里我帮你改成了15分，避开拥堵
    - cron: '15 1,5,10 * * *'
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          pip install requests
          pip install beautifulsoup4

      - name: Run script
        env:
          PUSHPLUS_TOKEN: ${{ secrets.PUSHPLUS_TOKEN }}
        run: python main.py
