import unittest
from you_get.common import any_download


class KuaishouTest(unittest.TestCase):

    def test_download(self):
        any_download('https://v.kuaishouapp.com/s/BO1I9zjn', merge=True, output_dir='.', info_only=False)
