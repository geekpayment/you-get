import unittest

from you_get.common import any_download


class WeishiTest(unittest.TestCase):

    def test_download(self):
        any_download('https://isee.weishi.qq.com/ws/app-pages/share/index.html?wxplay=1&id=7063hjISx1MevcsqS&collectionid=f54f57afd9ac265aaafd0caa5dc21cdb&spid=7557690793835499526&qua=v1_iph_weishi_8.30.2_230_app_a&chid=100081003&pkg=&attach=cp_reserves3_1000370721', merge=True, info_only=False, output_dir='.')
