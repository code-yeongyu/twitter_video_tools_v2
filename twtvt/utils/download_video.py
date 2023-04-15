from typing import Optional, Union

import typer
import yt_dlp
from playwright.sync_api import sync_playwright

from .twitter_parser import TwitterParser
from .url_validator import URLValidator


def download_video(
    target_links: list[str],
    username: str,
    password: str,
    output: str = 'videos',
    debug: bool = False,
    cookies_from_browser: Optional[str] = None,
    until_link: Optional[str] = None,
):

    # load playwright
    with sync_playwright() as playwright_sync:
        browser = playwright_sync.webkit.launch(headless=debug)
        page = browser.new_page()

        # load parser
        parser = TwitterParser(page)
        parser.login(username, password)

        # extract video links
        video_links: list[str] = []
        for target_link in target_links:
            url_validator = URLValidator(target_link)
            if not url_validator.is_valid_link():
                raise typer.BadParameter(f"'{target_link}' is an invalid link.")

            if url_validator.is_valid_twitter_media_link():
                target_username = target_link.split('/')[3]
                video_links.extend(parser.get_media_video_tweets_until(target_username, until_link or 'nothing'))
            elif url_validator.is_valid_twitter_liked_link():
                target_username = target_link.split('/')[3]
                video_links.extend(parser.get_liked_video_tweets_until(target_username, until_link or 'nothing'))
            else:
                video_links.append(target_link)

    # save video_links as links.txt as backup
    with open('links.txt', 'w') as f:
        f.write('\n'.join(video_links))

    ydl_opts: dict[str, Union[str, bool, tuple[Optional[str]]]] = {
        'embed_subs': True,
        'noplaylist': True,
        'nocheckcertificate': True,
    }
    ydl_opts['outtmpl'] = f'{output}/%(title)s.%(ext)s'
    ydl_opts['cookiesfrombrowser'] = (cookies_from_browser, )

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(video_links)
