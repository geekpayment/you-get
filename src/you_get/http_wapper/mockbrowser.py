import logging
import time
from typing import Union

import chromedriver_py as chrome
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class MockBrowser:
    _driver = None

    def __init__(self, url: str, ready_selector: str, debug=False):
        opt = webdriver.ChromeOptions()
        if not debug:
            opt.add_argument('--headless')
        opt.add_argument('--no-sandbox')
        opt.add_argument('--disable-gpu')
        opt.add_argument('--disable-dev-shm-usage')
        opt.add_argument('--disable-blink-features')
        opt.add_argument('--disable-blink-features=AutomationControlled')
        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.74 Safari/537.36 Edg/79.0.309.43'
        opt.add_argument(f'user-agent={ua}')
        opt.add_experimental_option('excludeSwitches', ['enable-automation'])
        opt.add_experimental_option('useAutomationExtension', False)
        self._driver = webdriver.Chrome(executable_path=chrome.binary_path, options=opt)
        self._driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator,"webdriver",{get:()=>undefined})'
        })
        self._driver.get(url)
        elem_present = EC.presence_of_element_located((By.CSS_SELECTOR, ready_selector))
        try:
            WebDriverWait(driver=self._driver, timeout=30).until(elem_present)
            time.sleep(1)
        except TimeoutException as e:
            logging.error('failed to open url or element not found', e)
            raise e

    def find_element(self, css_selector: str) -> Union[WebElement, None]:
        try:
            elem = self._driver.find_element_by_css_selector(css_selector)
        except NoSuchElementException as e:
            logging.error('not found element', e)
            return None
        else:
            return elem

    def xhr_request(self, url, method, data: str, headers: dict = None):
        if headers is None:
            headers = {}
        request_js = f'''
        function getVideoInfo() {{
        var xhr = new XMLHttpRequest();
        xhr.open('{method}','{url}',false);
        '''
        for k, v in headers.items():
            request_js += f'''
            xhr.setRequestHeader('{k}','{v}');
            '''
        request_js += f'''
        xhr.send('{data}')
        return xhr.response;
        }}
        return getVideoInfo()
        '''
        print(request_js)
        return self._driver.execute_script(request_js)

    @property
    def title(self):
        return self._driver.title

    @property
    def current_cookies(self):
        return self._driver.get_cookies()

    @property
    def current_cookie_str(self):
        _cookies = self.current_cookies
        return '; '.join([f"{cookie.get('name')}={cookie.get('value')}" for cookie in _cookies])

    @property
    def current_url(self):
        return self._driver.current_url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._driver.close()


if __name__ == '__main__':
    with MockBrowser(
            'https://v.kuaishouapp.com/s/BO1I9zjn',
            'video.player-video') as browser:
        elem = browser.find_element('video.player-video')
        title = browser.title

        cookies = browser.current_cookie_str
        src = elem.get_attribute('src')
        print(f'loaded: [{title}]:{src}')
        print('cookies:', cookies)
