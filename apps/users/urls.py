from django.conf.urls import include, url
from apps.users import views

app_name = 'users'

urlpatterns = [
    # url(r"^register/$", views.register, name='register' ),
    # url(r"^do_register/$", views.do_register, name='do_register' ),

    # 需要添加括号, 调用dispatch(), 判断get还是post, 返回一个函数，
    url(r'^register/$', views.RegisterView.as_view(), name='register'),

    #
    url(r'^active/(.+)$', views.ActiveView.as_view(), name='Active'),
]