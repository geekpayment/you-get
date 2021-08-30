import unittest
from you_get import YouGetDownloader
from you_get.common import DefaultProgressFactory


class PrintingProgressBar:
    _total_size = None
    _downloaded = None
    _total_pieces = None
    _current_piece = None

    def __init__(self, total_size, total_pieces):
        self._total_size = total_size
        self._total_pieces = total_pieces
        self._downloaded = 0
        self._current_piece = 0

    def update(self):
        if self._total_size is not None:
            print('downloaded %s' % int(self._downloaded * 100 / self._total_size))
        else:
            print('downloaded %s' % int(self._current_piece * 100 / self._total_pieces))

    def update_received(self, n):
        self._downloaded += n
        self.update()

    def update_piece(self, n):
        self._current_piece = n
        self.update()

    def done(self):
        self.update()


class PrintingProgressFactory(DefaultProgressFactory):
    def init_bar(self, size, pieces):
        return PrintingProgressBar(size, pieces)

    def init_no_size_bar(self, pieces):
        return PrintingProgressBar(None, pieces)


class MyTestCase(unittest.TestCase):
    def test_downloader(self):
        downloader = YouGetDownloader()
        downloader.config(progress_factory=PrintingProgressFactory())
        downloader.download('https://www.bilibili.com/video/BV14q4y1U763?spm_id_from=333.851.b_7265636f6d6d656e64.7')


if __name__ == '__main__':
    unittest.main()
