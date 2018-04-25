import time
from celery import Celery
from django.core.mail import send_mail
from django.shortcuts import render
from django.template import loader

from DailyFresh import settings

# # 在celery服务端初始化django环境
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DailyFresh.settings")
# import django
# django.setup()

# 创建celery客户端
from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods

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


@app.task
def generate_static_index_page():
    """生成静态页面"""
    # 防止数据库加载未完成就生成页面
    time.sleep(2)
    categories = GoodsCategory.objects.all()
    slide_skus = IndexSlideGoods.objects.all().order_by('index')
    promotions = IndexPromotion.objects.all().order_by('index')[0:2]
    # catagory_skus = IndexCategoryGoods.objects.all()[]
    for c in categories:
        # 查询当前类别所有的文字和图片商品
        text_skus = IndexCategoryGoods.objects.filter(display_type=0, category=c).order_by('index')

        image_skus = IndexCategoryGoods.objects.filter(display_type=1, category=c).order_by('index')[0:4]

        # 动态新增实例属性
        c.text_skus = text_skus
        c.image_skus = image_skus

    cart_count = 0

    context = {
        'categories': categories,
        'slide_skus': slide_skus,
        'promotions': promotions,
        'cart_count': cart_count
    }

    template = loader.get_template('index.html')
    html_str = template.render(context)
    # 生成的静态页面保存到桌面
    path = '/Users/mac/Desktop/static/index.html'
    with open(path, 'w') as f:
        f.write(html_str)
