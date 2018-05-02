from django.conf.urls import include, url

from apps.cart import views

urlpatterns = [
    # 进入到购物车页面
    url(r'^$', views.CartInfoView.as_view(), name='info'),

    # 添加商品到购物车
    url(r'^add$', views.AddCartView.as_view(), name='add'),

    # 购物车页面 数量改变
    url(r'^update$', views.CartUpdateView.as_view(), name='update'),

    # 购物车页面删除
    url(r'^delete', views.CartDeleteView.as_view(), name='delete'),

    # 立即购买
    url(r'^delete', views.CartDeleteView.as_view(), name='delete'),

]