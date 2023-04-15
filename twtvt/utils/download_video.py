import logging
import time
from typing import Iterable, Optional, Union

import yt_dlp
from playwright.sync_api import sync_playwright
from tenacity import after_log, before_sleep_log, retry, stop_after_attempt, wait_fixed

from .logger import logger
from .twitter_parser import TwitterParser
from .uri_validator import URIValidator


def download_video(
    target_uris: list[str],
    output: str = '.',
    until_link: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    cookies_from_browser: Optional[str] = None,
    debug: bool = False,
):
    _validate_target_uris(target_uris=target_uris)
    video_links: tuple[str] = (
        *_extract_from_file_paths(target_uris=target_uris),
        *_extract_from_twitter_links(
            target_uris=target_uris,
            username=username,
            password=password,
            until_link=until_link,
            debug=debug,
        ),
    )
    _backup_links(links=video_links, output=output)
    _download_videos(video_links=video_links, output=output, cookies_from_browser=cookies_from_browser)


def _validate_target_uris(target_uris: list[str]):
    for target_uri in target_uris:
        validators = [URIValidator.is_twitter_link, URIValidator.is_monsnode_link, URIValidator.is_file_path]
        if not any(validator(target_uri) for validator in validators):
            raise ValueError(f'Invalid target_uri: {target_uri}')


def _extract_from_twitter_links(
    target_uris: Iterable[str],
    username: Optional[str],
    password: Optional[str],
    until_link: Optional[str],
    debug: bool,
) -> list[str]:
    twitter_target_links = [target_uri for target_uri in target_uris if URIValidator.is_twitter_link(target_uri)]
    if not twitter_target_links:
        return []
    if not username or not password:
        raise ValueError('Username and password are required for twitter links.')

    twitter_video_links = []
    with sync_playwright() as playwright_sync:
        # load browser
        browser = playwright_sync.webkit.launch(headless=not debug)
        page = browser.new_page()

        # load parser
        twitter_parser = TwitterParser(page)
        twitter_parser.login(username, password)

        # extract video links
        for target_link in twitter_target_links:
            logger.info(f'Extracting video links from {target_link}')
            if URIValidator.is_media_link(target_link):
                target_username = target_link.split('/')[3]
                twitter_video_links.extend(
                    twitter_parser.get_media_video_tweets_until(target_username, until_link or ''))
            elif URIValidator.is_liked_link(target_link):
                target_username = target_link.split('/')[3]
                twitter_video_links.extend(
                    twitter_parser.get_liked_video_tweets_until(target_username, until_link or ''))
            else:
                twitter_video_links.append(target_link)
    return twitter_video_links


def _extract_from_file_paths(target_uris: Iterable[str]) -> list[str]:
    video_links = []
    file_paths = [target_uri for target_uri in target_uris if URIValidator.is_file_path(target_uri)]
    for file_path in file_paths:
        logger.info(f'Extracting video links from {file_path}')
        with open(file_path, 'r') as f:
            links_in_file = f.read().splitlines()
            video_links.extend(links_in_file)

    return video_links


def _backup_links(links: tuple[str], output: str):
    with open(f'{output}/links-{int(time.time())}-{len(links)}_videos.txt', 'w') as f:
        f.write('\n'.join(links))


def _download_videos(video_links: tuple[str], output: str, cookies_from_browser: Optional[str]):
    for index, video_link in enumerate(video_links):
        logger.info(f'Downloading video from {video_link} ({index + 1}/{len(video_links)})')
        _download_video(video_link, output, cookies_from_browser)


@retry(
    reraise=True,
    before_sleep=before_sleep_log(logger, logging.DEBUG),
    after=after_log(logger, logging.INFO),
    stop=stop_after_attempt(60),
    wait=wait_fixed(5),
)
def _download_video(video_link: str, output: str, cookies_from_browser: Optional[str]):
    ydl_opts: dict[str, Union[str, bool, tuple[Optional[str]]]] = {
        'nocheckcertificate': True,
    }
    ydl_opts['outtmpl'] = f'{output}/%(title)s.%(upload_date>%Y-%m-%d)s.%(id)s.%(ext)s'
    if cookies_from_browser:
        ydl_opts['cookiesfrombrowser'] = (cookies_from_browser, )  # noqa

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_link])
