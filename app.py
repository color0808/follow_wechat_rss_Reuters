import feedparser
import requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)

# 企业微信机器人 webhook
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=9a895067-7663-4169-ac17-a7697d2693fe"

# 要抓取的 RSS 源
RSS_FEEDS = {
    "rsshub://reuters/world": "https://rsshub.app/reuters/world",
    "rsshub://reuters/world/china": "https://rsshub.app/reuters/world/china",
    "rsshub://reuters/world/us": "https://rsshub.app/reuters/world/us",
    "buzzing": "https://reutersnew.buzzing.cc/feed.xml"
}

# 用于记录已发送的链接，避免重复
sent_links = set()

def get_source_label(source_url):
    if "buzzing" in source_url:
        return "Buzzing"
    elif "china" in source_url:
        return "路透中国"
    elif "us" in source_url:
        return "路透美国"
    elif "reuters" in source_url:
        return "路透国际"
    else:
        return "资讯"

def format_entry(entry, source_url):
    source = get_source_label(source_url)
    title = entry.get("title", "").strip()
    link = entry.get("link", "").strip()
    published = entry.get("published", "")

    # 格式化时间
    try:
        dt = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z")
        published_str = dt.strftime("%Y-%m-%d %H:%M")
    except:
        published_str = published  # 若出错则保留原始时间

    return f"【{source}】{title}\n🕒 {published_str}\n🔗 {link}"

def send_to_wechat(content):
    payload = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"[+] 推送成功: {response.status_code}")
    except Exception as e:
        print(f"[!] 推送失败: {e}")

def fetch_and_send():
    print("[*] 开始抓取 RSS 数据...")
    all_entries = []

    for name, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            link = entry.get("link", "")
            if link in sent_links:
                continue
            sent_links.add(link)
            all_entries.append((entry, url))

    if not all_entries:
        print("[*] 无新增内容")
        return

    # 只推送最近 10 条，防止消息太长
    latest = all_entries[:10]
    message = "\n\n".join([format_entry(e, url) for e, url in latest])
    send_to_wechat(message)

# 设置定时任务（每15分钟一次）
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_send, 'interval', minutes=15)
scheduler.start()

@app.route('/')
def index():
    return "Follow RSS to WeChat Bot is running."

if __name__ == '__main__':
    fetch_and_send()  # 启动时先跑一次
    app.run(host='0.0.0.0', port=10000)
