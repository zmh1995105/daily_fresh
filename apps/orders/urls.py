from django.conf.urls import include, url

from apps.orders import views

urlpatterns = [

    # /orders/place
    url(r'^place$', views.PlaceOrderView.as_view(), name='place'),

    # /orders/commit
    url(r'^commit$', views.CommitOrderView.as_view(), name='commit'),
]