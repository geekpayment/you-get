import json

from ..common import download_urls, print_info, playlist_not_supported, url_size, log
from ..http_wapper import MockBrowser

__all__ = ['xiaohongshu_download_by_url']


def xiaohongshu_download_by_url(url, info_only=False, **kwargs):
    with MockBrowser(url, 'video') as client:
        script = client.find_element('script[type="application/ld+json"]')
        info_str = script.get_attribute('innerHTML')
        video_tag = client.find_element('video')
        video_url = video_tag.get_attribute('src')
        info = json.loads(info_str)
        title = info.get('name')
        log.print_log(f'video url:{video_url}, title:{title}')
        size = url_size(video_url)
        video_format = 'mp4'
        print_info(site_info, title, video_format, size)
        if not info_only:
            download_urls([video_url], title, video_format, size, **kwargs)
    pass


site_info = "xiaohongshu.com"
download = xiaohongshu_download_by_url
download_playlist = playlist_not_supported('xiaohongshu')
