from django.contrib.auth.decorators import login_required
from django.views.generic import View


# class LoginRequiredView(View):
#     """登录检测视的类视图"""
#
#     # 原as_view 是一个类方法，需要将重写的类方法定义为as_view()
#     @classmethod
#     def as_view(cls, **initkwargs):
#         view = super().as_view(**initkwargs)
#         return login_required(view)


class LoginRequiredViewMixin(object):
    """登录检测视的类视图"""

    # 原as_view 是一个类方法，需要将重写的类方法定义为as_view()
    @classmethod
    def as_view(cls, **initkwargs):
        print()
        # 继承链往后找下一个类的，as_view
        view = super().as_view(**initkwargs)
        return login_required(view)


