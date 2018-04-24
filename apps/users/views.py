import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django_redis import get_redis_connection
from itsdangerous import  TimedJSONWebSignatureSerializer, SignatureExpired

# Create your views here.
from django.views.generic import View
from redis import StrictRedis

from DailyFresh import settings
from apps.goods.models import GoodsSKU
from apps.users.models import User, Address
from celery_task.tasks import send_active_mail
from utils.common import LoginRequiredViewMixin


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

        next = request.GET.get('next')

        if next:
            return redirect(next)

        # 响应请求

        return redirect(reverse("goods:index"))


class LogoutView(View):

    def get(self, request):
        """注销"""
        # 调用 django的logout，会清楚登录用户的id，session数据
        logout(request)

        return redirect(reverse("goods:index"))


class UserOrderView(LoginRequiredViewMixin, View):

    def get(self, request):

        # if not request.user.is_authenticated():
        #     return  render(request, 'login.html')



        return render(request, 'user_center_order.html', {"which_page": 2})

class UserInfoView(LoginRequiredViewMixin, View):

    def get(self, request):
        try:

            # 查询新增的地址
            address = Address.objects.filter(user=request.user).order_by('-create_time')[0]
            # address = request.user.address_set.latest('create_time')
        except:
            address = None

        # todo: 读取当前用户浏览记录
        strict_redis = get_redis_connection()  # type: StrictRedis
        # history_1 = [3, 1, 2]
        key = 'history_%s' % request.user.id
        # 从左往右取，去5个商品id
        sku_ids = strict_redis.lrange(key, 0 , 4)
        print(sku_ids)
        # 查询出的结果是[1, 2, 3]
        # good_list = GoodsSKU.objects.filter(id__in=sku_ids)

        # 解决：
        good_list = []
        for sku_id in sku_ids:
            good_list.append(GoodsSKU.objects.get(id=sku_id))

        context = {
            "which_page": 1,
            'address': address,
            # 系统会自动传
            'user': request.user,
            'good_list': good_list
        }
        return render(request, 'user_center_info.html', context)

class UserSiteView(LoginRequiredViewMixin, View):
    # 继承的类，先继承的在前面
    def get(self, request):
        try:

            # 查询新增的地址
            address = Address.objects.filter(user=request.user).order_by('-create_time')[0]
            # address = request.user.address_set.latest('create_time')
        except Exception as r:
            print(r)
            address = None

        context = {
            "which_page": 3,
            'address': address,
            # # 系统会自动传
            # 'user': request.user
        }
        return render(request, 'user_center_site.html', context)

    def post(self, request):

        # 获取post请求参数
        receiver = request.POST.get('receiver')
        detail_addr = request.POST.get('detail_addr')
        zip_code = request.POST.get('zip_code')
        mobile = request.POST.get('mobile')

        # 合法性校验
        if not all([receiver, detail_addr, zip_code, mobile]):
            return render(request, 'user_center_site.html', {'errmsg': "参数不能为空！"})

        # 新增一个地址, 创建对象时封装的方法
        Address.objects.create(
            receiver_name=receiver,
            receiver_mobile=mobile,
            detail_addr=detail_addr,
            zip_code=zip_code,
            user=request.user,
        )

        # 添加地址成功，返回当前页面，刷新数据

        return redirect(reverse('users:site'))


# @login_required
# def address(request):
#     return render(request, 'user_center_site.html', {"which_page": 1})