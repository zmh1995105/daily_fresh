from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods, GoodsSKU
from apps.users.models import User

class GetCartCountView(object):
    def get_cart_count(self, request):
        # todo: 读取用户车添加到购物车的商品总数量
        cart_count = 0
        if request.user.is_authenticated():
            # 已经登录
            strict_redis = get_redis_connection('default')  # type: StrictRedis
            # cart_1 = {1:2, 2:2}
            key = 'cart_%s' % request.user.id
            # 返回list类型，存储的是bytes
            vals = strict_redis.hvals(key)
            for count in vals:
                cart_count += int(count)
        return cart_count


class IndexView(View, GetCartCountView):
    def get2(self, request):
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

    def get(self, request):
        # 读取redis中的缓存数据
        context = cache.get('index_page_data')
        if not context:
            print('no cache!')
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
                context = {
                    'categories': categories,
                    'slide_skus': slide_skus,
                    'promotions': promotions,

                }

            cache.set('index_page_data', context, 60*30)
        else:
            print('use cache')

        cart_count = self.get_cart_count(request)

        # 给字典新增键值
        context['cart_count'] = cart_count
        # context.update({'cart_count': cart_count})

        return render(request, 'index.html', context)


class DetailView(View, GetCartCountView):
    def get(self, request, sku_id):
        # todo: 查询数据库数据

        try:
            # 查询商品sku
            sku = GoodsSKU.objects.get(id=sku_id)


        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 查询所有商品分类信息
        categories = GoodsCategory.objects.all()

        # 查询最新商品推荐
        new_skus = GoodsSKU.objects.filter(category=sku.category).order_by('-create_time')[0:2]

        # 如果已登录，查询购物车信息
        cart_count = self.get_cart_count(request)

        # todo: 查询其他规格商品

        other_skus = GoodsSKU.objects.filter(spu=sku.spu).exclude(id=sku_id)

        # todo: 保存用户浏览记录
        if request.user.is_authenticated():
            strict_redis = get_redis_connection()  # type: StrictRedis

            key = 'history_%s' % request.user.id
            # 删除表内已有的当前sku_id
            strict_redis.lrem(key, 0, sku_id)

            # 添加最新的sku_id到最前面
            strict_redis.lpush(key, sku_id)

            # 最多只保留5个元素
            strict_redis.ltrim(key, 0, 4)

        context = {
            'sku': sku,
            'categories': categories,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'other_skus': other_skus


        }
        return render(request,'detail.html', context)


class ListView(View, GetCartCountView):
    def get(self, request, category_id, page_num):
        """
        商品详情页
        :param request:
        :param category_id:
        :param page_num:
        :return:
        """

        # 获取参数
        sort = request.GET.get('sort')

        # 校验参数合法性
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return redirect(reverse("goods:index"))

        # 查询对应商品商品数据

        categories = GoodsCategory.objects.all()
        try:

            new_skus = GoodsSKU.objects.filter(category=category).order_by('-create_time')[0:2]

        except GoodsSKU:
            new_skus = None

        if sort in ['-sales', '-price']:
            skus = GoodsSKU.objects.filter(category=category).order_by(sort)

        else:
            skus = GoodsSKU.objects.filter(category=category)
            sort = 'default'

        cart_count = self.get_cart_count(request)

        # 显示对象 每页显示个数
        paginator = Paginator(skus, 4)
        try:
            page = paginator.page(page_num)

        except:
            page = paginator.page(1)


        context = {
            "category": category,
            "categories": categories,
            # 'skus': skus,
            'page': page,
            'page_range': paginator.page_range,
            'new_skus': new_skus,
            'sort': sort,
            'cart_count': cart_count,



        }
        return render(request, 'list.html', context)