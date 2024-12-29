# -*- coding: utf-8 -*-
import datetime
from sanic import Sanic
from sanic.response import json
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

app = Sanic("MyApp")

# 定义温湿度阈值
t_threshold = (25, 28)
h_threshold = (30, 33)

# 配置邮箱服务器信息
EMAIL_CONFIG = {
    "host": "smtp.qq.com",
    "port": 587,
    "username": "783016538@qq.com",
    "password": "ovakfbhgsvkqbeaf",
    "sender": "783016538@qq.com"
}

@app.route("/upload", methods=["POST"], name='upload')
@app.route("/invoke", methods=["POST"], name='invoke')
def data_upload(request):
    try:
        data = request.json
        sn = data.get("sn")
        temperature = data.get("temperature")
        humidity = data.get("humidity")

        if not all([sn, temperature, humidity]):
            return json({"error": "Missing required fields"}, status=400)

        # 判断温湿度是否超出阈值
        t_out_flag = not (t_threshold[0] <= temperature <= t_threshold[1])
        h_out_flag = not (h_threshold[0] <= humidity <= h_threshold[1])

        # 如果超出阈值，则生成邮件正文内容并发送带附件的邮件
        if t_out_flag or h_out_flag:
            email_body = generate_email_body(
                sn, temperature, humidity, t_threshold, h_threshold
            )
            file_path = generate_alert_file(sn, email_body)

            # 发送邮件，附加文件
            send_email_with_attachment(
                recipient="783016538@qq.com",
                subject="告警邮件 - 温湿度异常",
                body="设备温湿度异常，详见附件。",
                attachment_path=file_path
            )

            return json({"status": 1, "message": "异常", "data": {"file": file_path}})
        else:
            return json({"status": 0, "message": "正常"})

    except Exception as e:
        return json({"error": str(e)}, status=500)

# 生成告警文件
def generate_alert_file(sn, email_body):
    file_name = f"alert_{sn}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(email_body)
    return file_name

# 生成告警邮件正文
def generate_email_body(sn, temperature, humidity, t_threshold, h_threshold):
    return (
        f"设备序列号：{sn}\n\n"
        f"当前温度超出预设阈值范围：\n"
        f"实际温度：{temperature}℃\n"
        f"预设阈值范围：{t_threshold[0]}℃ - {t_threshold[1]}℃\n\n"
        f"当前湿度超出预设阈值范围：\n"
        f"实际湿度：{humidity}%\n"
        f"预设阈值范围：{h_threshold[0]}% - {h_threshold[1]}%\n\n"
        f"告警时间：{datetime.datetime.now().isoformat()}"
    )

# 定义发送带附件的邮件函数
def send_email_with_attachment(recipient, subject, body, attachment_path):
    # 创建邮件对象
    msg = MIMEMultipart()
    msg["From"] = EMAIL_CONFIG["sender"]
    msg["To"] = recipient
    msg["Subject"] = subject

    # 添加邮件正文
    msg.attach(MIMEText(body, "plain"))

    # 添加附件
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={os.path.basename(attachment_path)}",
    )
    msg.attach(part)

    # 连接SMTP服务器并发送邮件
    server = SMTP(EMAIL_CONFIG["host"], EMAIL_CONFIG["port"])
    server.starttls()  # 启用TLS加密
    server.login(EMAIL_CONFIG["username"], EMAIL_CONFIG["password"])
    server.send_message(msg)
    server.quit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
