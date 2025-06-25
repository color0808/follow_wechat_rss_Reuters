
# 多源 RSS → 企业微信 自动推送

本服务定时从多个 RSS 源抓取新闻更新，自动推送至企业微信群机器人。

## 📌 支持的源包括：
- https://rsshub.app/reuters/world
- https://rsshub.app/reuters/world/china
- https://rsshub.app/reuters/world/us
- https://reutersnew.buzzing.cc/feed.xml

## 🛠 部署方式（Render）

1. 登录 https://render.com
2. 创建 Web Service，绑定 GitHub 项目
3. 设置 Build Command: `pip install -r requirements.txt`
4. 设置 Start Command: `python app.py`
5. 服务上线后每 5 分钟自动轮询所有 RSS 源并推送

