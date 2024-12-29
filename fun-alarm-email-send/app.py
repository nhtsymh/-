# -*- coding: utf-8 -*-
import json as std_json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

from sanic import Sanic, response
from sanic.response import json

from email_config_service import (create_config,
                                  delete_config,
                                  read_config,
                                  update_config)
from users_service import (register_user,
                           delete_user,
                           update_user)                                  

app = Sanic("EmailSender")

# 发送邮件
async def send_email(data):
    # 从数据库中读取邮件配置
    email_config = await read_config(None)

    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = email_config["sender"]
    msg['To'] = data.get("recipient")
    msg['Subject'] = data.get("subject")

    # 添加邮件正文
    msg.attach(MIMEText(data.get("body"), 'plain'))

    # 连接SMTP服务器
    server = SMTP(email_config["host"], email_config["port"])
    server.starttls()  # 启动TLS加密
    server.login(email_config["username"], email_config["password"])

    # 发送邮件
    server.send_message(msg)

    # 关闭连接
    server.quit()
    return {"message": "Email sent successfully"}

async def login_user(data):
    # 从数据库中读取邮件配置
    email_config = await read_config(None)

    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = email_config["sender"]
    msg['To'] = data.get("recipient")
    msg['Subject'] = data.get("subject")

    # 添加邮件正文
    msg.attach(MIMEText(data.get("body"), 'plain'))

    # 连接SMTP服务器
    server = SMTP(email_config["host"], email_config["port"])
    server.starttls()  # 启动TLS加密
    server.login(email_config["username"], email_config["password"])

    # 发送邮件
    server.send_message(msg)

    # 关闭连接
    server.quit()
    return {"message": "User is attempting to login"}

# 定义路由
@app.route("/invoke", methods=["POST"])
async def send_email_route(request):
    action = request.json.get("action")
    data = request.json.get("data", {})

    actions = {
        "create_config": create_config,
        "read_config": read_config,
        "update_config": update_config,
        "delete_config": delete_config,
        "send_email": send_email,
        "register_user": register_user,
        "update_user": update_user,
        "delete_user": delete_user,
        "login_user": login_user
    }

    func = actions.get(action)
    if func:
        return json(await func(data))
    else:
        return response.json({"error": "Invalid action"}, status=400)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, dev=True)
