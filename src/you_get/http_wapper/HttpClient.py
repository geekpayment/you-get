import gzip
import io
import json
import logging
import re
import zlib
from typing import Dict
from urllib import request, error, parse

logger = logging.getLogger('HttpClient')

default_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.74 Safari/537.36 Edg/79.0.309.43'
fake_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    # noqa
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
}


class NoRedirection(request.HTTPErrorProcessor):
    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()

        # only add this line to stop 302 redirection.
        if code in [301, 302, 303, 307]:
            return response

        if not (200 <= code < 300):
            response = self.parent.error(
                'http', request, response, code, msg, hdrs)
        return response

    https_response = http_response


class HttpClient:
    _opener = None
    _cookies = {}
    _user_agent = None
    _last_response = None
    _current_url = None
    _upgrade_insecure_requests = False

    def __init__(self, user_agent: str = None, upgrade_insecure_requests=False):
        self._user_agent = user_agent or default_ua
        self._opener = request.build_opener(NoRedirection)
        self._upgrade_insecure_requests = upgrade_insecure_requests

    def _merge_headers(self, url, method, headers=None) -> Dict[str, str]:
        if headers is None:
            headers = fake_headers.copy()
        else:
            headers = fake_headers.copy().update(headers)
        if self._current_url is not None:
            headers['Referer'] = self._current_url
            url = parse.urlparse(self._current_url)
            headers['Origin'] = f'{url.scheme}://{url.hostname}'
        headers['User-Agent'] = self._user_agent
        if len(self._cookies) > 0:
            headers['Cookie'] = '; '.join([f"{key}={val}" for key, val in self._cookies.items()])
        if self._upgrade_insecure_requests:
            url_obj = parse.urlparse(url)
            if url_obj.scheme == 'http':
                headers[':scheme'] = 'https'
                headers[':method'] = method
                headers[':authority'] = url_obj.hostname
                headers[':path'] = url_obj.path + ('?' + url_obj.query if len(url_obj.query) > 0 else '')
                headers['upgrade-insecure-requests'] = '1'
        return headers

    def request(self, url, method='GET', data=None, headers=None, decoded=True):
        req_header = self._merge_headers(url, method, headers)
        data = self._encode_data(method, req_header, data)
        req = request.Request(url, method=method, headers=req_header, data=data)
        try:
            resp = self._opener.open(req)
        except error.HTTPError as e:
            err_info = e.read()
            err_msg = ''
            if err_info is not None:
                err_msg = err_info.decode('utf-8')
            msg = f'Http error:[{e.getcode()}]{err_msg}'
            logger.error(msg, e)
            raise e
        else:
            resp_header = resp.headers
            cookies = resp_header.get_all('set-cookie')
            if cookies is not None:
                for cookie in cookies:
                    self._read_cookie(cookie)
            if resp.code in [301, 302, 303, 307]:
                logger.debug('matched redirect, handling to %s' % url)
                url = resp_header.get('Location')
                target_location = parse.urljoin(resp.url, url)
                return self.request(target_location, method, data, headers, decoded)
            self._last_response = resp
            self._current_url = resp.url

            content_encoding = resp_header.get('Content-Encoding')
            data = resp.read()
            if content_encoding == 'gzip':
                data = ungzip(data)
            elif content_encoding == 'deflate':
                data = undeflate(data)
            if decoded:
                charset = match1(
                    resp_header.get('Content-Type', ''), r'charset=([\w-]+)'
                )
                if charset is not None:
                    data = data.decode(charset, 'ignore')
                else:
                    data = data.decode('utf-8', 'ignore')

            return data

    def _read_cookie(self, cookie_str: str):
        if cookie_str.count(';') > 0:
            cookie_str = cookie_str[0:cookie_str.index(';')]
        if cookie_str.count('=') > 0:
            self._cookies[cookie_str[0:cookie_str.index('=')]] = cookie_str[cookie_str.index('=') + 1:]
        else:
            self._cookies[cookie_str] = ''

    @property
    def current_cookies(self):
        return self._cookies

    @property
    def current_url(self):
        return self._current_url

    @staticmethod
    def _encode_data(method, headers, data):
        if method not in ['POST', 'PUT']:
            return None
        if data is None:
            return None
        if isinstance(data, dict):
            headers['Content-Type'] = 'application/json'
            return json.dumps(data).encode('utf-8')
        elif isinstance(data, str):
            return data.encode('utf-8')
        elif isinstance(data, bytes):
            return data
        else:
            raise TypeError(f'unsupported data type {type(data)}')


def ungzip(data):
    buffer = io.BytesIO(data)
    f = gzip.GzipFile(fileobj=buffer)
    return f.read()


def undeflate(data):
    decompressobj = zlib.decompressobj(-zlib.MAX_WBITS)
    return decompressobj.decompress(data) + decompressobj.flush()


def match1(text, *patterns):
    """Scans through a string for substrings matched some patterns (first-subgroups only).

    Args:
        text: A string to be scanned.
        patterns: Arbitrary number of regex patterns.

    Returns:
        When only one pattern is given, returns a string (None if no match found).
        When more than one pattern are given, returns a list of strings ([] if no match found).
    """

    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret
