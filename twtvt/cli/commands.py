from typing import Optional, Union

import typer
import yt_dlp
from playwright.sync_api import sync_playwright
from typer import Typer

from twtvt.utils import TwitterParser, URLValidator

cli_app = Typer()


@cli_app.command()
def twtvt(
    target_links: list[str] = typer.Argument(..., help="Video tweet link or target user's likes or media."),
    username: str = typer.Argument(..., help='Your twitter credentials username.'),
    password: str = typer.Option(..., help='Your twitter credentials password.'),
    cookies_from_browser: Optional[str] = typer.Option(None, help='Browser to get cookies from. '),
    output: str = typer.Option('videos', help='Output path for downloaded videos.'),
    debug: bool = typer.Option(False, help='Enable debug mode. This disables headless mode of Browser.'),
    until_link: Optional[str] = typer.Option(
        None,
        help="Keeps finding videos until this link is found. None for no limit. Only for user's likes or media.",
    ),
):

    # load playwright
    browser = sync_playwright().start().webkit.launch(headless=False)
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

    page.context.cookies()
    page.close()

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
