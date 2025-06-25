from flask import Flask, request, jsonify
import requests
import feedparser
import hashlib
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import time

app = Flask(__name__)

WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=9a895067-7663-4169-ac17-a7697d2693fe"
RSS_FEEDS = [
    "https://rsshub.app/reuters/world",
    "https://rsshub.app/reuters/world/china",
    "https://rsshub.app/reuters/world/us",
    "https://reutersnew.buzzing.cc/feed.xml"
]

posted_hashes = set()

def fetch_and_push():
    print("[INFO] 开始抓取 RSS 源")
    for url in RSS_FEEDS:
        try:
            print(f"[INFO] 抓取：{url}")
            feed = feedparser.parse(url)
            for entry in feed.entries:
                uid = hashlib.md5((entry.link + entry.title).encode('utf-8')).hexdigest()
                if uid not in posted_hashes:
                    content = {
                        "msgtype": "markdown",
                        "markdown": {
                            "content": f"### {entry.title}\n[阅读原文]({entry.link})"
                        }
                    }
                    resp = requests.post(WEBHOOK_URL, json=content)
                    if resp.status_code == 200:
                        print(f"[OK] 已推送：{entry.title}")
                        posted_hashes.add(uid)
                    else:
                        print(f"[ERROR] 推送失败：{resp.status_code}")
        except Exception as e:
            print(f"[ERROR] 抓取失败：{e}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_push, 'interval', minutes=5)
    scheduler.start()
    print("[INFO] 定时器已启动")

@app.route("/")
def index():
    return "RSS WeChat Pusher is running."

@app.route("/follow", methods=["POST"])
def follow_push():
    try:
        data = request.get_json(force=True)
        title = data.get("title", "No title")
        link = data.get("link", "#")
        print(f"[INFO] 收到 follow webhook：{title}")
        content = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"### {title}\n[阅读原文]({link})"
            }
        }
        resp = requests.post(WEBHOOK_URL, json=content)
        if resp.status_code == 200:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "failed", "code": resp.status_code}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    threading.Thread(target=start_scheduler).start()  # 后台线程启动定时器
    fetch_and_push()  # 启动时先执行一次
    app.run(host="0.0.0.0", port=10000)
