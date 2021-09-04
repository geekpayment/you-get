from .common import log, any_download, DefaultProgressFactory, config_env
import os
from datetime import datetime
from typing import Callable

__all__ = ['ProgressBundle', 'YouGetDownloader']


class ProgressBundle:
    _total_bytes = None
    _received_bytes = None
    _total_pieces = None
    _received_pieces = None
    _speed = None
    _finished = None

    def __init__(self, total_bytes, received, total_pieces, received_pieces, speed, finished):
        self._total_bytes = total_bytes
        self._received_bytes = received
        self._total_pieces = total_pieces
        self._received_pieces = received_pieces
        self._speed = speed
        self._finished = finished

    @property
    def total_bytes(self):
        return self._total_bytes

    @property
    def received_bytes(self):
        return self._received_bytes

    @property
    def total_pieces(self):
        return self._total_pieces

    @property
    def received_pieces(self):
        return self._received_pieces

    @property
    def speed(self):
        return self._speed

    @property
    def finished(self):
        return self._finished

    @property
    def percentage(self):
        if self._total_bytes is not None:
            return round(self._received_bytes / self._total_bytes * 100, 2)
        else:
            return round(self._received_pieces / self._total_pieces * 100, 2)


class ProgressWithTrigger:
    _progress_callback: Callable[[ProgressBundle], None] = None
    _total_piece = None
    _total_size = None
    _last_update = None
    _downloaded_size = None
    _current_piece = None
    _speed = None
    _finished = None

    def __init__(self, progress_callback: Callable[[ProgressBundle], None], total_piece, total_size=None):
        self._progress_callback = progress_callback
        self._total_piece = total_piece
        self._total_size = total_size
        self._downloaded_size = 0
        self._current_piece = 0
        self._finished = False

    def update(self):
        self._progress_callback(
            ProgressBundle(self._total_size, self._downloaded_size, self._total_piece, self._current_piece, self._speed,
                           self._finished))

    def update_received(self, n):
        self._downloaded_size += n
        now = datetime.now()
        if self._last_update is not None:
            byte_ps = n / (now - self._last_update).total_seconds()
            self._speed = round(byte_ps, 2)
        self._last_update = now

        self.update()

    def update_piece(self, n):
        self._current_piece = n
        self.update()

    def done(self):
        if not self._finished:
            self._downloaded_size = self._total_size
            self._finished = True
            self.update()


class ProgressWithTriggerFactory(DefaultProgressFactory):
    _callback: Callable[[ProgressBundle], None] = None

    def __init__(self, callback: Callable[[ProgressBundle], None]):
        self._callback = callback

    def init_bar(self, size, pieces):
        return ProgressWithTrigger(self._callback, total_piece=pieces, total_size=size)

    def init_no_size_bar(self, pieces):
        return ProgressWithTrigger(self._callback, total_piece=pieces)


class YouGetDownloader:
    _output_dir = None

    def __init__(self, output_dir='.'):
        self._output_dir = os.path.abspath(output_dir)
        log.d(f'configured output dir {self._output_dir}')
        self._progress_factory = DefaultProgressFactory()

    def config(self, output_dir: str = None):
        if output_dir is not None:
            self._output_dir = os.path.abspath(output_dir)
            log.d(f'configured output dir {self._output_dir}')

    def download(self, url, progress_callback: Callable[[ProgressBundle], None] = None,
                 video_info_callback: Callable[[dict], None] = None, **kwargs):
        """
        video info callback:
        {
            "title": "video title",
            "site_info": "site",
            "size": 1000,
            "type": "video_type"
        }
        """
        if progress_callback is not None:
            config_env(progress_fact=ProgressWithTriggerFactory(progress_callback),
                       video_info_callback=video_info_callback)
        any_download(url, merge=True, output_dir=self._output_dir, info_only=False, **kwargs)
