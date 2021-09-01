import unittest

from you_get import YouGetDownloader


class MyTestCase(unittest.TestCase):
    def test_downloader(self):
        downloader = YouGetDownloader()
        downloader.download('https://www.bilibili.com/video/BV14q4y1U763?spm_id_from=333.851.b_7265636f6d6d656e64.7',
                            lambda progress: print(f'downloaded {progress.percentage}%'))


if __name__ == '__main__':
    unittest.main()
