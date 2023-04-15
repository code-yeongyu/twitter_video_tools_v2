from typing import Optional

import typer
from typer import Typer

from twtvt.utils import download_video

cli_app = Typer()


@cli_app.command()
def twtvt(
    target_links: list[str] = typer.Argument(..., help="Video tweet link or target user's likes or media."),
    username: str = typer.Argument(..., help='Your twitter credentials username.'),
    password: str = typer.Argument(..., help='Your twitter credentials password.'),
    cookies_from_browser: Optional[str] = typer.Option(None, help='Browser to get cookies from. '),
    output: str = typer.Option('videos', help='Output path for downloaded videos.'),
    debug: bool = typer.Option(False, help='Enable debug mode. This disables headless mode of Browser.'),
    until_link: Optional[str] = typer.Option(
        None,
        help="Keeps finding videos until this link is found. None for no limit. Only for user's likes or media.",
    ),
):
    download_video(
        target_links=target_links,
        username=username,
        password=password,
        output=output,
        debug=debug,
        cookies_from_browser=cookies_from_browser,
        until_link=until_link,
    )
