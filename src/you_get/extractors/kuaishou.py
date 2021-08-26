#!/usr/bin/env python

import urllib.request
import urllib.parse
import json
from ..http_wapper import HttpClient
import re

from ..util import log
from ..common import download_urls, print_info, playlist_not_supported, url_size

__all__ = ['kuaishou_download_by_url']


def kuaishou_download_by_url(url, info_only=False, **kwargs):
    client = HttpClient()
    client.request(url)
    last_url = client.current_url
    url_obj = urllib.parse.urlparse(last_url)
    match = re.findall(r'/short-video/(\w+)', url_obj.path)
    photo_id = match[0]
    area_query = urllib.parse.parse_qs(url_obj.query).get('area')
    area = area_query[0] if area_query is not None else None
    variables = dict(photoId=photo_id, page='detail')
    if area is not None:
        variables['webPageArea'] = area
    ajax_data = dict(
        operationName='visionVideoDetail',
        query="query visionVideoDetail($photoId: String, $type: String, $page: String, $webPageArea: String) {\n  visionVideoDetail(photoId: $photoId, type: $type, page: $page, webPageArea: $webPageArea) {\n    status\n    type\n    author {\n      id\n      name\n      following\n      headerUrl\n      __typename\n    }\n    photo {\n      id\n      duration\n      caption\n      likeCount\n      realLikeCount\n      coverUrl\n      photoUrl\n      liked\n      timestamp\n      expTag\n      llsid\n      viewCount\n      videoRatio\n      stereoType\n      croppedPhotoUrl\n      manifest {\n        mediaType\n        businessType\n        version\n        adaptationSet {\n          id\n          duration\n          representation {\n            id\n            defaultSelect\n            backupUrl\n            codecs\n            url\n            height\n            width\n            avgBitrate\n            maxBitrate\n            m3u8Slice\n            qualityType\n            qualityLabel\n            frameRate\n            featureP2sp\n            hidden\n            disableAdaptive\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    tags {\n      type\n      name\n      __typename\n    }\n    commentLimit {\n      canAddComment\n      __typename\n    }\n    llsid\n    danmakuSwitch\n    __typename\n  }\n}\n",
        variables=variables
    )
    try:
        graph_resp = client.request(f'{url_obj.scheme}://{url_obj.hostname}/graphql', method='POST', data=ajax_data)
        video_detail = json.loads(graph_resp)
        photo = video_detail.get('data').get('visionVideoDetail').get('photo')
        all_video_infos = photo.get('manifest').get('adaptationSet')
        title = photo.get('caption')
        video_url = all_video_infos[0].get('representation')[0].get('url')
        size = url_size(video_url)
        video_format = video_url[:video_url.index('?')].split('.')[-1] if video_url.count('?') > 0 else \
            video_url.split('.')[-1]
        print_info(site_info, title, video_format, size)
        if not info_only:
            download_urls([video_url], title, video_format, size, **kwargs)
    except:
        og_image_url = re.search(r"<meta\s+property=\"og:image\"\s+content=\"(.+?)\"/>", page).group(1)
        image_url = og_image_url
        title = url.split('/')[-1]
        size = url_size(image_url)
        image_format = image_url.split('.')[-1]
        print_info(site_info, title, image_format, size)
        if not info_only:
            download_urls([image_url], title, image_format, size, **kwargs)
    # result wrong size


site_info = "kuaishou.com"
download = kuaishou_download_by_url
download_playlist = playlist_not_supported('kuaishou')
