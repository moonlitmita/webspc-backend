# webspc-backend

# Project Introduction

## WebSPC transforms conventional SPC from “after-the-fact chart viewing” into a 7×24 AI Quality Co-Pilot—self-collecting data, self-detecting anomalies, 

## self-diagnosing root causes, and @-tagging you with the conclusions.

## Key Features:

1.Embedded LLM dialog engine plus MCP tool chain—ask the model to analyze SPC data in plain language and watch it invoke MCP tools to carry out any
follow-up task.

2.Dynamic, periodic tasks can be added on the fly for real-time data ingestion from any third-party database.

3.LLM-powered real-time streaming monitor: the instant an anomaly appears, root-cause analysis kicks in and a recommended action plan is pushed to the

Feishu(Lark) group, @-tagging the right people and slashing response time.

# Open-source repository:

1. Front-end business code address: https://gitee.com/valleyfo/webspc-frontend

2. General back-end business code address: https://gitee.com/valleyfo/webspc-backend

3. AI back-end business code address: https://gitee.com/valleyfo/webspc-ai

# Project Architecture

Framework: Flask

Database: MySQL

ORM Framework: SQLAlchemy

Task Queue System: Celery

Language: Python

# 1.Instructional Video:

- [01.WebSPC使用方法介绍](https://www.bilibili.com/video/BV1h1XRYLEUt/?spm_id_from=333.1387.collection.video_card.click&vd_source=690fc386f07d30bd01bc5ca11d98ecf3)

- [02.WebSPC使用方法补充-数据自动采集](https://www.bilibili.com/video/BV1ANQbY9EpH?spm_id_from=333.788.recommend_more_video.1&vd_source=690fc386f07d30bd01bc5ca11d98ecf3)

# 2.Project Deployment Video:

- [01.WebSPC项目部署_01](https://www.bilibili.com/video/BV11RQAYWE82/?spm_id_from=333.1387.collection.video_card.click&vd_source=690fc386f07d30bd01bc5ca11d98ecf3)

- [02.WebSPC项目部署_02](https://www.bilibili.com/video/BV1EmQwYgEJt/?spm_id_from=333.1387.collection.video_card.click&vd_source=690fc386f07d30bd01bc5ca11d98ecf3)

Supplement:
When building the backend Docker image, switch the code from development to production mode by:
Uncommenting the last line in manage.py (flask_app.run).
Commenting out the line immediately above it.

# 3.Development Environment Setup

## 3.1 Clone
git clone https://gitee.com/valleyfo/webspc-backend.git

## 3.2 Create Virtual Env
conda create -n myenv python=3.11 -y

## 3.3 Activate Env
conda activate myenv

## 3.5 Install Packages
pip install -r requirements.txt

## 3.6 Set Env Variables (PowerShell)
$env:FLASK_APP = "RealProject"

$env:FLASK_ENV = "development" 

# 4. Live Demo

URL: https://webspc.top

Username, Password: Contact the author

# 5. Technical Support

Author: valleyfo

Email: wynmamtf@163.com

QQ: 271989251

Wexin: valleyfo

Note: Technical support includes but is not limited to:
Custom business development
Project deployment
Application explanation and so on