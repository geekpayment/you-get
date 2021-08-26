from you_get.http_wapper import MockBrowser
from urllib import parse
from you_get.common import match1
import json

if __name__ == '__main__':
    with MockBrowser(
            'https://isee.weishi.qq.com/ws/app-pages/share/index.html?wxplay=1&id=7063hjISx1MevcsqS&collectionid=f54f57afd9ac265aaafd0caa5dc21cdb&spid=7557690793835499526&qua=v1_iph_weishi_8.30.2_230_app_a&chid=100081003&pkg=&attach=cp_reserves3_1000370721',
            'iframe') as cli:
        url = cli.current_url
        parsed = parse.urlparse(url)
        vid = match1(parsed.path, r'/weishi/feed/(\w+)/wsfeed')
        req_data = dict(datalvl='all', feedid=vid, recommendtype=0, _weishi_mapExt={})
        data_str = cli.xhr_request('/webapp/json/weishi/WSH5GetPlayPage', 'POST', json.dumps(req_data),headers={'Content-Type':'application/json'})
        print(f'fetch response= {data_str}')
        data = json.loads(data_str)
        feed0 = data.get('data').get('feeds')[0]
        title = feed0.get('material_desc')
        url = feed0.get('video_url')
        print(f'[{title}] {url}')
