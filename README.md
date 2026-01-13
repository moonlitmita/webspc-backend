# webspc-backend

# 项目介绍

## WebSPC把传统SPC从“事后看图”升级成“7×24 的 AI 质量副驾驶”——会自己采数、自己判异、自己找根因，还能把结论 @ 你。

## 特色功能：

### 1. 集成了LLM对话引擎及MCP工具链,不但可以让LLM对SPC数据进行分析，还可以调用MCP工具链执行特定任务。

### 2. 支持动态添加周期性任务，对第三方数据库进行实时数据采集。

### 3.LLM实时流式监控，异常一出现，立即执行根因分析，并将处理建议自动推到飞书群，@相关责任人，大大提高异常响应时间。

# 开源地址：
   
1. 前端业务代码地址：https://gitee.com/valleyfo/webspc-frontend

2. 常规后端业务代码地址：https://gitee.com/valleyfo/webspc-backend

3. AI后端业务代码地址:https://gitee.com/valleyfo/webspc-ai

# 项目架构

    框架: Flask

    数据库：MySQL

    ORM框架：SQLAlchemy

    任务队列系统：Celery

    语言：Python

# 1.使用方法视频：

[01.WebSPC使用方法介绍](https://www.bilibili.com/video/BV1h1XRYLEUt/?spm_id_from=333.1387.collection.video_card.click&vd_source=690fc386f07d30bd01bc5ca11d98ecf3)

[02.WebSPC使用方法补充-数据自动采集](https://www.bilibili.com/video/BV1ANQbY9EpH?spm_id_from=333.788.recommend_more_video.1&vd_source=690fc386f07d30bd01bc5ca11d98ecf3)

# 2.项目部署视频：

[01.WebSPC项目部署_01](https://www.bilibili.com/video/BV11RQAYWE82/?spm_id_from=333.1387.collection.video_card.click&vd_source=690fc386f07d30bd01bc5ca11d98ecf3)

[02.WebSPC项目部署_02](https://www.bilibili.com/video/BV1EmQwYgEJt/?spm_id_from=333.1387.collection.video_card.click&vd_source=690fc386f07d30bd01bc5ca11d98ecf3)

补充：

在构建后端镜像的过程中，需要将代码从开发模式调整到生产模式：

将manage.py中的最后一行注释解锁(flask_app.run)，该行代码的上面一行代码注释。

## 3.环境配置

需要配置以下环境变量：

- `FLASK_ENV`: 运行环境（生产环境为production）
- `FLASK_APP`: FLASK 入口文件
- `SQLALCHEMY_DATABASE_URI`: 项目数据库的URI地址
- `FIRST_DATABASE_URI`: 第一个外部数据库的URI地址
- `JWT_SECRET`: jwt令牌密码，用于用户身份认证
- `CELERY_BROKER_URL`: Celery 任务栈URL
- `CELERY_RESULT_BACKEND`: Celery 存储结果的URL

# 2.开发环境配置：

## 2.1 克隆项目到指定文件夹
git clone https://gitee.com/valleyfo/webspc-backend.git

## 2.2 创建虚拟环境
conda create -n myenv python=3.11 -y

## 2.3 激活虚拟环境
conda activate myenv

## 2.4 安装依赖
pip install -r requirements.txt

## 2.5 注入环境变量(powershell)

$env:FLASK_APP = "RealProject"

$env:FLASK_ENV = "development" 

## 2.6 修改MySQL数据库密码为实际的密码

在安装完mysql和redis后：

在RealProject文件夹下的settings.py中的get_db_uri函数中的root后的密码变更为实际的密码。

## 2.7 执行以下命令启动程序
python manage.py

# 3.项目演示地址：https://webspc.top

用户名，密码：联系作者获取

# 4.技术服务：

作者：valleyfo

Email: wynmamtf@163.com

QQ: 271989251

Weixin: valleyfo

备注：技术服务包括但不限于
    定制业务开发,
    项目部署,
    应用讲解等。


