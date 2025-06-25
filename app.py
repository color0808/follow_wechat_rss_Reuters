from flask import Flask, request
import requests
import feedparser
from apscheduler.schedulers.background import BackgroundScheduler
import os

app = Flask(__name__)

WECHAT_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=9a895067-7663-4169-ac17-a7697d2693fe"
RSS_URLS = [
    "https://rsshub.app/reuters/world",
    "https://rsshub.app/reuters/world/china",
    "https://rsshub.app/reuters/world/us",
    "https://reutersnew.buzzing.cc/feed.xml"
]
SEEN_LINKS = set()

@app.route("/")
def index():
    return "Multi RSS to WeChat Bot is running.", 200

@app.route("/follow", methods=["POST"])
def follow_update():
    data = request.json or {}
    title = data.get("title", "RSS 有更新")
    url = data.get("url", "")
    content = f"📢 RSS 更新通知：\n\n标题：{title}\n链接：{url}"

    resp = requests.post(WECHAT_WEBHOOK, json={
        "msgtype": "text",
        "text": {"content": content}
    })

    return "Pushed", resp.status_code

def check_rss():
    try:
        for rss_url in RSS_URLS:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:5]:
                if entry.link not in SEEN_LINKS:
                    SEEN_LINKS.add(entry.link)
                    payload = {"title": entry.title, "url": entry.link}
                    requests.post("http://localhost:5000/follow", json=payload)
    except Exception as e:
        print("RSS fetch error:", str(e))

scheduler = BackgroundScheduler()
scheduler.add_job(check_rss, 'interval', minutes=5)
scheduler.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
