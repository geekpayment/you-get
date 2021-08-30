from .common import log, any_download, DefaultProgressFactory, config_env
import os


class YouGetDownloader:
    _output_dir = None
    _progress_factory = None

    def __init__(self, output_dir='.'):
        self._output_dir = os.path.abspath(output_dir)
        log.d(f'configured output dir {self._output_dir}')
        self._progress_factory = DefaultProgressFactory()

    def config(self, output_dir: str = None, progress_factory: DefaultProgressFactory = None):
        if output_dir is not None:
            self._output_dir = os.path.abspath(output_dir)
            log.d(f'configured output dir {self._output_dir}')
        if progress_factory is not None:
            self._progress_factory = progress_factory

    def download(self, url):
        config_env(progress_fact=self._progress_factory)
        any_download(url, merge=True, output_dir=self._output_dir, info_only=False)
