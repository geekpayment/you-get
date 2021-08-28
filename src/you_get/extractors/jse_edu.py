from ..common import playlist_not_supported, url_size, print_info, download_urls, general_m3u8_extractor
from ..http_wapper import HttpClient
from urllib import parse
import json
import random
import string


def jse_edu_download(url, info_only, **kwargs):
    parsed = parse.urlparse(url)
    resource_id = parse.parse_qs(parsed.query).get('resource_id')[0]
    cli = HttpClient()
    detail_resp = cli.request(f'{parsed.scheme}://{parsed.hostname}/baseApi/seyk/resource/detail/', 'POST',
                              f'resource_id={resource_id}',
                              headers={'Content-Type': 'application/x-www-form-encoded'})
    detail_json = json.loads(detail_resp)
    resource_info = detail_json.get('data').get('resource_info')
    file_id = resource_info.get('file_id')
    title = resource_info.get('title')

    base_vod_resp = cli.request(f'{parsed.scheme}://{parsed.hostname}/baseApi/base/vod/', 'POST',
                                f'file_id={file_id}',
                                headers={'Content-Type': 'application/x-www-form-encoded'})
    base_vod_json = json.loads(base_vod_resp)
    appid = base_vod_json.get('data').get('app_id')
    psign = base_vod_json.get('data').get('psign')
    overlay_key = ''.join(random.choices(string.hexdigits, k=32))
    overlay_iv = ''.join(random.choices(string.hexdigits, k=32))
    common_headers = {'Referer': f'{parsed.scheme}://{parsed.hostname}/',
                      'Origin': f'{parsed.scheme}://{parsed.hostname}'}
    m3u8 = cli.request(
        f'https://playvideo.qcloud.com/getplayinfo/v4/{appid}/{file_id}?psign={psign}&overlayKey={overlay_key}&overlayIv={overlay_iv}',
        method='GET',
        headers=common_headers)
    print(f'm3u8 resp:{m3u8}')
    m3u8_json = json.loads(m3u8)
    plain_output = m3u8_json.get('media').get('streamingInfo').get('plainOutput')
    sub_streams = plain_output.get('subStreams')
    max_area = 0
    max_area_index = 0
    for idx, sub_stream in enumerate(sub_streams):
        area = int(sub_stream.get('width')) * int(sub_stream.get('height'))
        if max_area < area:
            max_area = area
            max_area_index = idx

    m3u8_url = plain_output.get('url')
    urls = general_m3u8_extractor(m3u8_url, common_headers)
    target_m3u8 = urls[max_area_index]
    v_urls = general_m3u8_extractor(target_m3u8, common_headers)
    size = sum([url_size(url, headers=common_headers) for url in v_urls])
    print_info(site_info, title, 'mp4', size)
    if not info_only:
        download_urls(v_urls, title, 'mp4', size, **kwargs)


site_info = 'jse.edu.cn'
download = jse_edu_download
download_playlist = playlist_not_supported('jse_edu')
