import unittest
from you_get.common import any_download


class JseEduTest(unittest.TestCase):

    def test_download(self):
        any_download('https://mskzkt.jse.edu.cn/cloudCourse/seyk/detail.php?resource_id=12961', output_dir='.',
                     merge=True, info_only=False)
