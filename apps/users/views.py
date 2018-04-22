import re

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from itsdangerous import  TimedJSONWebSignatureSerializer, SignatureExpired

# Create your views here.
from django.views.generic import View

from DailyFresh import settings
from apps.users.models import User
from celery_task.tasks import send_active_mail


def register(request):

    return render(request, 'register.html')


def do_register(request):
    """实现注册功能"""
    # 获取post请求参数
    username = request.POST.get('username')
    password = request.POST.get('password')
    password2 = request.POST.get('password2')
    email = request.POST.get('email')
    allow = request.POST.get('allow')  # 勾选为on

    # todo: 校验参数合法性

    # 判断参数不为空
    if not all([username, password, password2, email, allow]):
        return render(request, 'register.html', {'errmsg': '参数不能为空'})

    if password != password2:
        return render(request, 'register.html', {'errmsg': '两次输入密码不一致'})

    # 判断邮箱合法
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request, 'register.html', {'errmsg': '密码不合法'})

    # 判断是否勾选用户协议
    if allow != 'on':
        return render(request, 'register.html', {'errmsg': '为勾选用户协议'})

    try:

        # 处理业务： 保存用户到数据表中
        user = User.objects.create_user(username, email, password)

        # 修改用户状态为未激活，默认激活
        user.is_active = False
        user.save()

    except IntegrityError:
        # 判断用户是否存在
        return render(request, 'register.html', {'errmsg': '用户已经存在'})

    # todo: 发送激活邮件

    # 响应请求
    return HttpResponse('registered successfully!')


class RegisterView(View):
    def get(self,  request):
        return render(request, 'register.html')

    def post(self, request):
        """实现注册功能"""
        # 获取post请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        allow = request.POST.get('allow')  # 勾选为on
        user = None # type: User

        # todo: 校验参数合法性

        # 判断参数不为空
        if not all([username, password, password2, email, allow]):
            return render(request, 'register.html', {'errmsg': '参数不能为空'})

        if password != password2:
            return render(request, 'register.html', {'errmsg': '两次输入密码不一致'})

        # 判断邮箱合法
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '密码不合法'})

        # 判断是否勾选用户协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '为勾选用户协议'})

        try:

            # 处理业务： 保存用户到数据表中
            user = User.objects.create_user(username, email, password)

            # 修改用户状态为未激活，默认激活
            user.is_active = False
            user.save()

        except IntegrityError:
            # 判断用户是否存在
            return render(request, 'register.html', {'errmsg': '用户已经存在'})

        # 发送激活邮件
        token = user.generate_active_token()

        # 同步发送： 会阻塞
        # RegisterView.send_active_mail(username, email, token)

        # celery异步发送
        send_active_mail.delay(username, email, token)

        # 响应请求
        return HttpResponse('registered successfully!')

    @staticmethod
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


class ActiveView(View):

    def get(self, request, token: str):
        """

        :param request:
        :param token: 对字典{'confirm': user.id}加密后得到的字符串
        :return:
        """
        try:

            # 解密token
            s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY)
            # str -> bytes
            dict_data = s.loads(token.encode())

        except SignatureExpired:
            # 判断是否失效
            return HttpResponse('激活链接已失效！')

        # 获取用户id
        user_id = dict_data.get('confirm')

        # 修改为已激活
        User.objects.filter(id=user_id).update(is_active=True)

        return HttpResponse('激活成功，跳转到登录界面')


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 获取post请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        # 验证合法性
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '用户名/密码不能为空'})

        # 业务处理：login
        user = authenticate(username=username, password=password)

        # 判断密码是否正确
        if user is None:
            return render(request, 'login.html', {'errmsg': '用户名/密码不正确'})

        # 判断是否激活
        if not user.is_active:
            return render(request, 'login.html', {'errmsg': '用户未激活'})

        # 登陆成功，保存用户登录状态
        # request.session['auth_user_id'] = user.id
        # user.reqest.user
        login(request, user)


        # 0 关闭浏览器失效； None 两周失效
        if remember != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)

        # 响应请求


        return redirect(reverse("goods:index"))


class LogoutView(View):

    def get(self, request):
        """注销"""
        # 调用 django的logout，会清楚登录用户的id，session数据
        logout(request)

        return redirect(reverse("goods:index"))