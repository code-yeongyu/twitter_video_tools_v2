from enum import Enum
from http.cookiejar import CookieJar
from typing import Callable, Optional, cast

import browser_cookie3


class SupportedBrowser(Enum):
    '''Supported browsers for cookie extraction.'''

    CHROME = 'chrome'
    FIREFOX = 'firefox'
    OPERA = 'opera'
    OPERA_GX = 'opera gx'
    EDGE = 'edge'
    CHROMIUM = 'chromium'
    BRAVE = 'brave'
    VIVALDI = 'vivaldi'
    SAFARI = 'safari'


def get_cookie_loader(browser_name: Optional[SupportedBrowser], ) -> Callable[[str], CookieJar]:
    if not browser_name:
        return browser_cookie3.load
    if browser_name == SupportedBrowser.CHROME:
        return browser_cookie3.chrome
    if browser_name == SupportedBrowser.FIREFOX:
        return browser_cookie3.firefox
    if browser_name == SupportedBrowser.OPERA:
        return browser_cookie3.opera
    if browser_name == SupportedBrowser.OPERA_GX:
        return browser_cookie3.opera_gx
    if browser_name == SupportedBrowser.EDGE:
        return browser_cookie3.edge
    if browser_name == SupportedBrowser.CHROMIUM:
        return browser_cookie3.chromium
    if browser_name == SupportedBrowser.BRAVE:
        return browser_cookie3.brave
    if browser_name == SupportedBrowser.VIVALDI:
        return browser_cookie3.vivaldi
    if browser_name == SupportedBrowser.SAFARI:
        return browser_cookie3.safari
    raise ValueError(f'Unsupported browser: {browser_name}')


def load_cookies(browser_name: Optional[SupportedBrowser] = None, domain: str = '') -> CookieJar:
    cookie_loader = get_cookie_loader(browser_name=browser_name)
    all_cookies = cast(CookieJar, cookie_loader())
    if not domain:
        return all_cookies

    return [cookie for cookie in all_cookies if cookie.domain.endswith(f'{domain}')]
