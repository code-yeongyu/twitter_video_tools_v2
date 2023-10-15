from enum import Enum
from http.cookiejar import CookieJar
from typing import Callable, Optional

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


def get_cookie_loader(browser_name: Optional[SupportedBrowser]) -> Callable[[str], CookieJar]:

    def wrapper(domain: str) -> CookieJar:
        if browser_name == SupportedBrowser.CHROME:
            return browser_cookie3.chrome(domain)
        if browser_name == SupportedBrowser.FIREFOX:
            return browser_cookie3.firefox(domain)
        if browser_name == SupportedBrowser.OPERA:
            return browser_cookie3.opera(domain)
        if browser_name == SupportedBrowser.OPERA_GX:
            return browser_cookie3.opera_gx(domain)
        if browser_name == SupportedBrowser.EDGE:
            return browser_cookie3.edge(domain)
        if browser_name == SupportedBrowser.CHROMIUM:
            return browser_cookie3.chromium(domain)
        if browser_name == SupportedBrowser.BRAVE:
            return browser_cookie3.brave(domain)
        if browser_name == SupportedBrowser.VIVALDI:
            return browser_cookie3.vivaldi(domain)
        if browser_name == SupportedBrowser.SAFARI:
            return browser_cookie3.safari(domain)
        return browser_cookie3.load(domain)

    return wrapper


def load_cookies(browser_name: Optional[SupportedBrowser] = None, domain: str = '') -> CookieJar:
    cookie_loader = get_cookie_loader(browser_name=browser_name)
    all_cookies = cookie_loader(domain)
    if not domain:
        return all_cookies

    filtered_jar = CookieJar()
    for cookie in all_cookies:
        if cookie.domain.endswith(f'{domain}'):
            filtered_jar.set_cookie(cookie)
    return filtered_jar
