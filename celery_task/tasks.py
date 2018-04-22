from celery import Celery
from django.core.mail import send_mail

from DailyFresh import settings

# 创建celery客户端
app = Celery('dailyfresh', broker='redis://127.0.0.1:6379/1')


@app.task
def send_active_mail(username, email, token):
    """发送激活邮件"""

    # subject, message, from_email, recipient_list,
    # fail_silently = False, auth_user = None, auth_password = None,
    # connection = None, html_message = None

    subject = '天天生鲜激活邮件'
    message = ''
    from_email = settings.EMAIL_FROM
    recipient_list = [email]
    html_message = ('<h2>尊敬的 %s, 感谢注册天天生鲜</h2>'
                    '<p>请点击此链接激活您的帐号: '
                    '<a href="http://127.0.0.1:8000/users/active/%s">'
                    'http://127.0.0.1:8000/users/active/%s</a>'
                    ) % (username, token, token)
    send_mail(subject, message, from_email, recipient_list, html_message=html_message)

