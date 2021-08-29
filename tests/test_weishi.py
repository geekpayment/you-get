import unittest

from you_get.common import any_download


class WeishiTest(unittest.TestCase):

    def test_download(self):
        any_download('https://www.bilibili.com/video/BV14v411W7F8?p=1&share_medium=iphone&share_plat=ios&share_session_id=9E81771B-C798-47AB-A238-29AED9C5CF3F&share_source=WEIXIN&share_tag=s_i&timestamp=1630235462&unique_k=5eOjdD', merge=True, info_only=False, output_dir='.')
