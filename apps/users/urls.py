from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required

from apps.users import views

app_name = 'users'

urlpatterns = [
    # url(r"^register/$", views.register, name='register' ),
    # url(r"^do_register/$", views.do_register, name='do_register' ),

    # 需要添加括号, 调用dispatch(), 判断get还是post, 返回一个函数，
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),

    # 激活功能
    url(r'^active/(.+)$', views.ActiveView.as_view(), name='Active'),

    # 用户中心
    url(r'^orders$', views.UserOrderView.as_view(), name='orders'),
    url(r'^$', views.UserInfoView.as_view(), name='info'),
    url(r'^site$', views.UserSiteView.as_view(), name='site'),
    # url(r'^site$', views.address, name='site'),

    # url(r'^site$', login_required(views.UserSiteView.as_view()), name='site'),



]