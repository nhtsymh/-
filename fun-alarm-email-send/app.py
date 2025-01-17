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


async def enhanced_register_user(data):
    # 调用注册用户服务
    result = await register_user(data)

    # 如果注册成功，发送通知邮件
    if "message" in result and result["message"] == "User registered successfully":
        email_data = {
            "recipient": "783016538@qq.com",  # 使用用户注册的邮箱
            "subject": "Registration Successful",
            "body": f"Hello {data['username']},\n\nYour registration was successful.\n\nThank you!"
        }
        await send_email(email_data)
    
    return result



async def enhanced_delete_user(data):

    try:
        # 调用原始删除用户服务
        result = await delete_user(data)

        # 如果删除成功，发送通知邮件
        if "message" in result and result["message"] == "User deleted successfully":
            email_data = {
                "recipient": "783016538@qq.com",  # 替换为用户的邮箱
                "subject": "Account Deletion Successful",
                "body": f"Hello {data.get('username', 'User')},\n\nYour account has been successfully deleted.\n\nThank you!"
            }
            await send_email(email_data)

        return result
    except ValueError as ve:
        # 捕获 ValueError 并返回友好的错误消息
        return {"error": str(ve)}
    except Exception as e:
        # 捕获其他异常
        return {"error": f"An unexpected error occurred: {str(e)}"}




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
        "register_user": enhanced_register_user,
        "update_user": update_user,
        "delete_user": enhanced_delete_user,
        "login_user": login_user
    }

    func = actions.get(action)
    if func:
        return json(await func(data))
    else:
        return response.json({"error": "Invalid action"}, status=400)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, dev=True)

