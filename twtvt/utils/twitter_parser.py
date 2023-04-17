import time
from typing import Optional

from playwright.sync_api import Error, Page, Request

from twtvt.utils.logger import logger


class TwitterParser:
    page: Page

    def __init__(self, page: Page):
        self.page = page

    @property
    def page_current_height(self) -> int:
        current_height: int = self.page.evaluate('(window.innerHeight + window.scrollY)')
        return current_height

    def login(self, username: str, password: str, timeout: Optional[float] = 10000) -> None:
        logger.info('Logging in...')
        self.page.goto('https://twitter.com/i/flow/login')
        self.page.wait_for_selector('label:has-text(\"Phone, email, or username\") div >> nth=1')
        self.page.get_by_label('Phone, email, or username').click()
        self.page.get_by_label('Phone, email, or username').fill(username)
        self.page.get_by_label('Phone, email, or username').press('Enter')
        try:
            password_input = self.page.get_by_label('Password', exact=True)
            password_input.fill(password, timeout=timeout)
            password_input.press('Enter')
        except Error as error:
            raise ValueError('Login failed; Maybe username or password is incorrect?') from error
        self.page.wait_for_url('https://twitter.com/home')
        logger.info('Logged in successfully.')

    def get_all_liked_video_tweets(self, username: str, scroll_timeout: float = 0.8) -> list[str]:
        """Get the username's all liked tweets
        Returns the list of links of liked tweets
        """
        return self.get_liked_video_tweets_until(
            username, 'nothing', scroll_timeout
        )  # 'nothing' was intended because the given `until_link` would be never found on the links list

    def get_liked_video_tweets_until(self, username: str, until_link: str, scroll_timeout: float = 0.8) -> list[str]:
        '''Scrolling down the list of liked tweets until the given `until_link` found
        Returns the list of links of liked tweets
        '''
        self._goto_liked_tweets(username)
        links: list[str] = []

        previous_height = self.page_current_height
        while True:
            # 1. scroll down
            # 2. get the link of tweets in the current screen(tweets are not reachable if it's not rendering)
            # 3. break if page reaches to the bottom or the given `until_link` found

            self.page.mouse.wheel(0, 1500)
            time.sleep(scroll_timeout)  # wait for mouse wheel to scroll down
            is_page_bottom = self.page_current_height == previous_height
            if is_page_bottom:
                logger.debug('Reached to the bottom of the liked tweets.')
                break
            previous_height = self.page_current_height

            new_links = self._get_video_tweets_in_current_screen()
            links.extend(new_links)
            links = list(set(links))

            logger.debug(f'Found {len(links)} liked tweets.')

            if until_link in links:
                logger.debug("Found the given 'until_link' in the liked tweets.")
                break

        return links

    def get_recent_liked_tweet(self, username: str) -> str:
        self._goto_liked_tweets(username)
        return self._get_tweets_in_current_screen()[0]

    def _get_tweets_in_current_screen(self) -> list[str]:
        links: list[str] = []

        while True:
            articles = self.page.locator('article')
            article_length = articles.count()
            try:
                links = [
                    'https://twitter.com' +
                    (articles.nth(i).locator('div').locator('a').nth(3).get_attribute('href', timeout=500) or '')
                    for i in range(article_length)
                ]
                break
            except Error:  # if articles in the page are not reachable
                logger.debug('Articles are not reachable. Update scroll position.')
                self.page.mouse.wheel(0, 500)  #  scrolling down to refresh the articles
                self.page.mouse.wheel(0, -500)  #  scrolling down to refresh the articles

        return links

    def get_video_of_tweet(self, link: str, timeout: Optional[float] = 10000) -> list[tuple[str, str]]:
        video_links: list[str] = []

        def _request_m3u8_capture_handler(request: Request) -> None:
            if 'm3u8' in request.url:
                video_links.append(request.url)

        self.page.on('request', _request_m3u8_capture_handler)
        self.page.goto(link)
        try:
            self.page.wait_for_selector('video', timeout=timeout)
        except Error:
            return []

        return [(f'{self._parse_tweet_name()}_{index}.mp4', link) for index, link in enumerate(video_links)]

    def _parse_tweet_name(self) -> str:
        uploader = self.page.get_by_test_id('primaryColumn').get_by_role('link').nth(0).inner_text().strip()
        content = self.page.get_by_role('article').get_by_test_id('tweetText').nth(0).inner_text().strip()
        return f'{uploader} - {content}'

    def _goto_liked_tweets(self, username: str) -> None:
        self.page.goto(f'https://twitter.com/{username}/likes')
        self.page.wait_for_selector('article')

    def get_all_media_video_tweets(self, username: str, scroll_timeout: float = 0.8) -> list[str]:
        """Get the username's all liked tweets
        Returns the list of links of liked tweets
        """
        return self.get_media_video_tweets_until(
            username, 'nothing', scroll_timeout
        )  # 'nothing' was intended because the given `until_link` would be never found on the links list

    def get_media_video_tweets_until(self, username: str, until_link: str, scroll_timeout: float = 0.8) -> list[str]:
        '''Scrolling down the list of media tweets until the given `until_link` found
        Returns the list of links of media tweets
        '''
        self._goto_media_tweets(username)
        links: list[str] = []

        previous_height = self.page_current_height
        while True:
            # 1. scroll down
            # 2. get the link of tweets in the current screen(tweets are not reachable if it's not rendering)
            # 3. break if page reaches to the bottom or the given `until_link` found

            self.page.mouse.wheel(0, 1500)
            time.sleep(scroll_timeout)  # wait for mouse wheel to scroll down
            is_page_bottom = self.page_current_height == previous_height
            if is_page_bottom:
                break
            previous_height = self.page_current_height

            new_links = self._get_video_tweets_in_current_screen()
            links.extend(new_links)
            links = list(set(links))

            logger.debug(f'Found {len(links)} video tweets.')

            if until_link in links:
                break

        return links

    def _goto_media_tweets(self, username: str) -> None:
        self.page.goto(f'https://twitter.com/{username}/media')
        self.page.wait_for_selector('article')

    def _get_video_tweets_in_current_screen(self) -> list[str]:
        links: list[str] = []

        while True:
            articles = self.page.locator('article:has(video)')
            article_length = articles.count()
            try:
                links = [
                    'https://twitter.com' +
                    (articles.nth(i).locator('div').locator('a').nth(3).get_attribute('href', timeout=500) or '')
                    for i in range(article_length)
                ]
                break
            except Error:  # if articles in the page are not reachable
                self.page.mouse.wheel(0, 500)  #  scrolling down to refresh the articles
                self.page.mouse.wheel(0, -500)  #  scrolling down to refresh the articles

        return links
