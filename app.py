from pathlib import Path

# 生成更新后的app.py内容，使用用户指定的精简格式
app_py_content = '''
import feedparser
import requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# 企业微信Webhook地址
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=9a895067-7663-4169-ac17-a7697d2693fe"

# RSS订阅源列表
RSS_FEEDS = [
    "https://rsshub.app/reuters/world",
    "https://rsshub.app/reuters/world/china",
    "https://rsshub.app/reuters/world/us",
    "https://reutersnew.buzzing.cc/feed.xml"
]

# 存储已发送文章链接，避免重复发送
sent_entries = set()

def fetch_and_push():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            if entry.link in sent_entries:
                continue
            sent_entries.add(entry.link)
            # 构造精简格式推送内容
            content = f"【{feed.feed.title}】{entry.title}\\n📅 {entry.published}\\n🔗 {entry.link}"
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            try:
                requests.post(WEBHOOK_URL, json=data)
            except Exception as e:
                print("推送失败:", e)

# 定时任务：每30分钟检查一次新文章
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_push, 'interval', minutes=30)
scheduler.start()

@app.route('/')
def index():
    return "Follow.is → 企业微信机器人 推送器"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
'''

# 写入到本地文件
output_path = "/mnt/data/app.py"
Path(output_path).write_text(app_py_content)

output_path
