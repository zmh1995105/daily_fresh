from datetime import datetime
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsSKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
from utils.common import LoginRequiredViewMixin


class PlaceOrderView(LoginRequiredViewMixin, View):
    def post(self, request):
        # 获取请求参数：sku_ids, count
        sku_ids = request.POST.getlist('sku_ids')
        count = request.POST.get('count')
        print(count)

        # 校验参数合法性
        if not sku_ids:
            return redirect(reverse('cart:info'))

        # todo: 查询数据：地址，购物车商品，总数量，总额
        try:
            address = Address.objects.filter(user=request.user).latest('create_time')
        except:
            address = None

        strict_redis = get_redis_connection()  # type: StrictRedis
        key = 'cart_%s' % request.user.id
        skus = []
        total_count = 0
        total_amount = 0

        # 判断是否从购物车页面访问, count is None
        if count is None:
            for sku_id in sku_ids:
                try:
                    sku = GoodsSKU.objects.get(id=sku_id)

                except GoodsSKU.DoesNotExist:
                    return redirect(reverse('cart:info'))

                count = strict_redis.hget(key, sku_id)  # bytes
                count = int(count)
                amount = sku.price * count

                # 给商品id新增两个属性
                sku.count = count
                sku.amount = amount

                # 添加商品到列表
                skus.append(sku)

                # 累加总数量和总额
                total_count += count
                total_amount += amount

        # 从detail.html访问
        else:
            sku_id = request.POST.get('sku_ids')

            try:
                sku = GoodsSKU.objects.get(id=sku_id)

            except GoodsSKU.DoesNotExist:

                return redirect(reverse('cart:info'))

            count = int(count)

            if count > sku.stock:
                return redirect(reverse('goods:detail', args=[sku_id]))
            amount = sku.price * count

            # 给商品id新增两个属性
            sku.count = count
            sku.amount = amount

            # 添加商品到列表
            skus.append(sku)

            # 累加总数量和总额
            total_count += count
            total_amount += amount
            strict_redis.hset(key, sku_id, count)

        trans_cost = 10
        total_pay = total_amount + trans_cost
        sku_ids_str = ','.join(sku_ids)
        context = {
            'trans_cost': trans_cost,
            'total_amount': total_amount,
            'total_count': total_count,
            'total_pay': total_pay,
            'skus': skus,
            'address': address,
            'sku_ids_str': sku_ids_str
        }

        return render(request, 'place_order.html', context)


class CommitOrderView(View):
    @transaction.atomic
    def post(self, request):
        # 返回json数据，需要login判断
        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'errmsg': '请先登录！'})

        # 获取请求参数：address_id, pay_method, sku_ids_str
        address_id = request.POST.get('address_id')
        pay_method = request.POST.get('pay_method')
        # 格式如下：1，2，3
        sku_ids_str = request.POST.get('sku_ids_str')

        # 校验参数不能为空
        if not all([address_id, pay_method, sku_ids_str]):
            return JsonResponse({'code': 2, 'errmsg': '参数不完整！'})

        # 判断地址是否存在
        try:
            address = Address.objects.get(id=address_id)

        except Address.DoesNotExist:
            return JsonResponse({'code': 3, 'errmsg': '地址不能为空！'})

        # 创建保存点
        point1 = transaction.savepoint()
        try:

            # todo: 修改订单信息表: 保存订单数据到订单信息表中
            total_count = 0
            total_amount = 0
            trans_cost = 10

            order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(request.user.id)
            order = OrderInfo.objects.create(
                order_id=order_id,
                total_count=total_count,
                total_amount=total_amount,
                pay_method=pay_method,
                user=request.user,
                address=address,
                trans_cost=trans_cost
            )

            # 从Redis查询出购物车数据
            # 注意: 返回的是字典, 键值都为bytes类型
            # cart_1 = {1: 2, 2: 2}
            strict_redis = get_redis_connection('default')  # type: StrictRedis
            key = 'cart_%s' % request.user.id
            sku_ids = sku_ids_str.split(',')  # str -> list

            # todo: 核心业务: 遍历每一个商品, 并保存到订单商品表
            for sku_id in sku_ids:
                # 查询订单中的每一个商品
                try:
                    sku = GoodsSKU.objects.get(id=sku_id)
                except GoodsSKU.DoesNotExist:

                    transaction.savepoint_rollback(point1)
                    return JsonResponse({'code': 4, 'errmsg': '商品不存在！'})


                # 获取商品数量，并判断库存
                count = int(strict_redis.hget(key, sku_id))
                if count > sku.stock:
                    transaction.savepoint_rollback(point1)
                    return JsonResponse({'code': 5, 'errmsg': '库存不足！'})

                # todo: 修改订单商品表: 保存订单商品到订单商品表
                OrderGoods.objects.create(
                    count=count,
                    price=sku.price,
                    sku=sku,
                    order=order
                )

                # todo: 修改商品sku表: 减少商品库存, 增加商品销量
                sku.stock -= count
                sku.sales += count
                sku.save()

                # 累加商品数量和总金额
                total_count += count
                total_amount += count * sku.price

            # todo: 修改订单信息表: 修改商品总数量和总金额
            order.total_amount = total_amount
            order.total_count = total_count
            order.save()
        except:
            transaction.savepoint_rollback(point1)
            return JsonResponse({'code': 6, 'msg': '创建订单错误！'})

        # 从Redis中删除购物车中的商品
        # cart_1 = {1: 2, 2: 2}
        # redis命令: hdel cart_1 1 2
        # 直接列表 -> 位置参数，传入
        strict_redis.hdel(key, *sku_ids)

        # 订单创建成功， 响应请求，返回json
        return JsonResponse({'code': 0, 'msg': '创建订单成功！'})
