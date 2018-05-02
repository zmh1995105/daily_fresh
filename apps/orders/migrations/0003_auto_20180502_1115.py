# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20180422_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='trade_no',
            field=models.CharField(verbose_name='支付编号', max_length=100, blank=True, null=True, default=''),
        ),
    ]
