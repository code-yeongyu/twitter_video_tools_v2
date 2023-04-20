import logging
import time
from multiprocessing import cpu_count as get_cpu_count
from typing import Any, Iterable, Optional

import yt_dlp
from playwright.sync_api import sync_playwright
from rich.progress import Progress
from tenacity import after_log, before_sleep_log, retry, stop_after_attempt, wait_fixed

from twtvt.utils.execute_parallel import execute_parallel

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
    parallel: bool = False,
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
    if parallel:
        _download_videos_parallel(video_links=video_links, output=output, cookies_from_browser=cookies_from_browser)
    else:
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
    with Progress() as progress:
        video_download_task = progress.add_task('Downloading Videos', total=len(video_links))
        for index, video_link in enumerate(video_links):
            progress.update(video_download_task, advance=1)
            try:
                _download_video(video_link, output, cookies_from_browser, (index, len(video_links)))
            except Exception as e:
                logger.error(f'Failed to download video from {video_link}: {e}')


def _download_videos_parallel(video_links: tuple[str], output: str, cookies_from_browser: Optional[str]):
    args = [(video_link, output, cookies_from_browser) for video_link in video_links]

    with Progress() as progress:
        video_download_task = progress.add_task('Downloading Videos', total=len(args))
        for _ in execute_parallel(_download_video, args):
            progress.update(video_download_task, advance=1)
            progress.refresh()


@retry(
    reraise=True,
    before_sleep=before_sleep_log(logger, logging.DEBUG),
    after=after_log(logger, logging.INFO),
    stop=stop_after_attempt(60),
    wait=wait_fixed(10),
)
def _download_video(
    video_link: str,
    output: str,
    cookies_from_browser: Optional[str],
    counters: Optional[tuple[int, int]] = None,
):
    nothing_logger = logging.getLogger('nothing')
    nothing_logger.setLevel(logging.CRITICAL)
    ydl_opts: dict[str, Any] = {
        'nocheckcertificate': True,
        'concurrent_fragment_downloads': get_cpu_count() + 1,
        'outtmpl': f'{output}/%(title).200B.%(upload_date>%Y-%m-%d)s.%(id)s.%(ext)s',
        'no_warnings': True,
        'logger': nothing_logger,
    }
    if cookies_from_browser:
        ydl_opts['cookiesfrombrowser'] = (cookies_from_browser, )  # noqa

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result: dict[str, str] = ydl.extract_info(video_link, download=True)  # type: ignore
            if counters:
                logger.info(
                    f"[{counters[0]+1}/{counters[1]}] Downloaded video [magenta]{result['title']}[/]",
                    extra={'markup': True},
                )
            else:
                logger.info(f"Downloaded video [magenta]{result['title']}[/]", extra={'markup': True})
            return result
    except yt_dlp.utils.DownloadError as e:
        if '429' in str(e):  # Check if the error message contains "Too Many Requests"
            logger.info('Too many requests. Waiting for 5 minutes and retrying...')
            time.sleep(60 * 5)
            raise e  # Raise the exception to retry
