from django.shortcuts import render

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsCategory, IndexSlideGoods, IndexPromotion, IndexCategoryGoods
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

        cart_count = self.get_cart_count(request)



        context = {
            'categories': categories,
            'slide_skus': slide_skus,
            'promotions': promotions,
            'cart_count': cart_count
        }
        return render(request, 'index.html', context)


