from django.core.files.storage import FileSystemStorage
from fdfs_client.client import Fdfs_client


class FdfsStorage(FileSystemStorage):
    def _save(self, name, content):
        """
        当管理员在后台上传文件时，会使用此类保存上传的文件
        :param name:
        :param content: 返回一个
        :return:
        """

        # 默认保存在此路径下
        # path = super().save(name, content)
        # print(name, path, type(content))

        # todo: 保存到FastDfs服务器上
        client = Fdfs_client('utils/fdfs/client.conf')
        try:
            # 上传文件到服务器, 二进制
            datas = content.read()
            # 上传成功返回json字符串
            result = client.upload_appender_by_buffer(datas)
            status = result.get('Status')
            if status == 'Upload successed.':
                # 上传成功
                path = result.get('Remote file_id')
            else:
                raise  Exception('上传图片失败：%s' % status)
        except Exception as e:
            print(e)
        return path

    def url(self, name):
        path = super().url(name)
        return "http://192.168.49.131:8888/" + path



