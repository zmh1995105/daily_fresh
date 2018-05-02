from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis
from utils.common import LoginRequiredViewMixin

from apps.goods.models import GoodsSKU


class AddCartView(View):
    def post(self, request):
        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'errmsg': '请登录！！'})

        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        if not all([sku_id, count]):
            return JsonResponse({'code': 2, 'errmsg': '参数不完整！'})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code': 3, 'errmsg': '查找不到该商品！'})

        try:
            count = int(count)
        except:
            return JsonResponse({'code': 4, 'errmsg': '数量必须为整数！'})

        # cart_1 = {1:2, 2:2}
        strict_redis = get_redis_connection('default')  # type: StrictRedis
        key = 'cart_%s' % request.user.id

        # 购物车已有的商品数量
        value = strict_redis.hget(key, sku_id)  # byte

        # 如果购物车已存在该商品，则添加
        if value:
            count += int(value)

        if count > sku.stock:

            return JsonResponse({'code': 5, 'errmsg': '库存不足！'})
        # 修改redis数据
        strict_redis.hset(key, sku_id, count)

        # 计算并返回购物车总商品数
        total_count = 0
        vals = strict_redis.hvals(key)
        for val in vals:
            total_count += int(val)
        return JsonResponse({'code': 0, 'total_count': total_count})


class CartInfoView(LoginRequiredViewMixin, View):
    def get(self, request):

        user_id = request.user.id
        strict_redis = get_redis_connection('default')  # type: StrictRedis

        # 查询所有商品
        key = "cart_%s" % user_id
        sku_ids = strict_redis.hkeys(key)  # list(bytes)
        skus = []
        total_count = 0
        total_amount = 0
        for sku_id in sku_ids:

            sku = GoodsSKU.objects.get(id=int(sku_id))

            # todo: 增加实例属性，计算数量和金额
            sku.count = int(strict_redis.hget(key, sku_id))
            sku.amount = sku.count * sku.price
            total_count += sku.count
            total_amount += sku.amount
            skus.append(sku)


        context = {
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
        }
        return render(request, 'cart.html', context)


class CartUpdateView(View):
    def post(self, request):
        """修改商品数量"""
        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'errmsg': '请先登录！'})
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        if not all([sku_id, count]):
            return JsonResponse({'code': 2, 'errmsg': '参数不完整！'})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code': 3, 'errmsg': '查找不到该商品！'})

        try:
            count = int(count)
        except:
            return JsonResponse({'code': 4, 'errmsg': '数量必须为整数！'})

        if count > sku.stock:
            return JsonResponse({'code': 5, 'errmsg': '库存不足！！'})


        strict_redis = get_redis_connection('default')  # type: StrictRedis
        key = 'cart_%s' % request.user.id
        # 修改redis数据
        strict_redis.hset(key, sku_id, count)

        # 计算并返回购物车总商品数
        total_count = 0
        vals = strict_redis.hvals(key)
        for val in vals:
            total_count += int(val)
        print(total_count)
        return JsonResponse({'code': 0, 'total_count': total_count})


class CartDeleteView(View):
    def post(self, request):
        # 判断是否登录
        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'errmsg': '请先登录！'})

        # 接收参数：sku_id
        sku_id = request.POST.get('sku_id')

        # 校验参数：not，判断是否为空
        if not sku_id:
            return JsonResponse({'code': 2, 'errmsg': '参数不完整！'})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except:
            return JsonResponse({'code': 3, 'errmsg': '查找不到该商品！'})

        # 如果用户登陆，删除redis中购物车数据
        strict_redis = get_redis_connection('default')  # type: StrictRedis
        key = 'cart_%s' % request.user.id
        strict_redis.hdel(key, sku_id)

        total_count = 0
        vals = strict_redis.hvals(key)
        for val in vals:
            total_count += int(val)

        return JsonResponse({'code': 0, 'total_count': total_count})


