
from django.contrib import admin
from django.core.cache import cache

from apps.goods.models import *
from celery_task.tasks import *

class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        print('save mode: %s' % obj)
        # celery异步生成静态页面
        generate_static_index_page.delay()
        cache.delete('index_page_data')


    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        print('delete mode: %s' % obj)
        generate_static_index_page.delay()
        cache.delete('index_page_data')


class GoodsCategoryAdmin(BaseAdmin):
    pass


class GoodsImageAdmin(BaseAdmin):
    pass


class GoodsSKUAdmin(BaseAdmin):
    pass


class GoodsSPUAdmin(BaseAdmin):
    pass


class IndexCategoryGoodsAdmin(BaseAdmin):
    pass


class IndexPromotionAdmin(BaseAdmin):
    pass


class IndexSlideGoodsAdmin(BaseAdmin):
    pass


admin.site.register(GoodsCategory, GoodsCategoryAdmin)
admin.site.register(GoodsImage, GoodsImageAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(GoodsSPU, GoodsSPUAdmin)
admin.site.register(IndexCategoryGoods, IndexCategoryGoodsAdmin)
admin.site.register(IndexPromotion, IndexPromotionAdmin)
admin.site.register(IndexSlideGoods, IndexSlideGoodsAdmin)

