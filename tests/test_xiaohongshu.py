import unittest

from you_get.common import any_download


class XiaohongshuTest(unittest.TestCase):

    def test_download(self):
        any_download('http://xhslink.com/NMPXSd', merge=True, info_only=False, output_dir='.')
