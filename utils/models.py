from django.db import models

class BaseModel(models.Model):
    """模型类父类"""

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True