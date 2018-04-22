from django.shortcuts import render

# Create your views here.
from django.views.generic import View

from apps.users.models import User


class IndexView(View):
    def get(self, request):
        # 方式1：主动查询登录用户并显示
        # user_id = request.session.get('_auth_user_id')
        # user = User.objects.get(id=user_id)
        #
        # context = {
        #     'user': user
        # }
        # 方式2：使用django用户验证模块
        # django 自动查询登录页面，只要登录了就会保存在request页面中
        # user = request.user

        return render(request, 'index.html')