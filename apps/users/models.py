
from django.contrib.auth.models import AbstractUser
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer

# Create your models here.
from tinymce.models import HTMLField

from DailyFresh import settings
from utils.models import BaseModel


class User(BaseModel, AbstractUser):
    """用户模型类"""
    def generate_active_token(self):
        """对字典数据{'confirm': 10}加密，返回加密结果"""

        # 加密时间一天
        s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 60*60*24)

        datas = s.dumps({'confirm': self.id})  # type: bytes

        # byte -> str
        return datas.decode()

    class Meta(object):
        db_table = 'df_user'


class Address(BaseModel):
    """地址"""

    receiver_name = models.CharField(max_length=20, verbose_name="收件人")
    receiver_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    detail_addr = models.CharField(max_length=256, verbose_name="详细地址")
    zip_code = models.CharField(max_length=6, null=True, verbose_name="邮政编码")
    is_default = models.BooleanField(default=False, verbose_name='默认地址')

    user = models.ForeignKey(User, verbose_name="所属用户")

    class Meta:
        db_table = "df_address"


class TestModel(BaseModel):
    name = models.CharField(max_length=20)

    goods_detail = HTMLField(verbose_name='商品详情', null=True)