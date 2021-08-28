import unittest

from you_get.common import any_download
import tempfile
import os
from datetime import datetime
import random
import string

output_dir = os.path.join(tempfile.gettempdir(),
                          str(datetime.now().timestamp()) + '-' + ''.join(
                              random.choices(string.ascii_lowercase, k=5)))

os.mkdir(output_dir)
print(f'output dir {output_dir}')

class SitesTest(unittest.TestCase):

    def test_xiaohongshu(self):
        any_download('http://xhslink.com/NMPXSd', merge=True, info_only=False, output_dir=output_dir)

    def test_douyin(self):
        any_download('https://www.douyin.com/video/6970224863818566923?previous_page=main_page&tab_name=home',
                     merge=True, info_only=False, output_dir=output_dir)

    def test_bilibili(self):
        any_download('https://www.bilibili.com/video/BV1sy4y1575V?spm_id_from=333.851.b_7265636f6d6d656e64.3', merge=True, info_only=False, output_dir=output_dir)


if __name__ == '__main__':
    print(f'output dir{output_dir}')
    unittest.main()
    for file in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, file))
    os.rmdir(output_dir)
