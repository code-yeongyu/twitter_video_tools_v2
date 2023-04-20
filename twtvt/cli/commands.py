from typing import Optional

import typer
from typer import Typer

from twtvt.utils import download_video

cli_app = Typer()


@cli_app.command()
def twtvt(
        target_uris: list[str] = typer.Argument(
            ...,
            help="Video tweet link, target user's likes or media, or file path.",
        ),
        username: Optional[str] = typer.Option(None, help='Your twitter credentials username.'),
        password: Optional[str] = typer.Option(None, help='Your twitter credentials password.'),
        cookies_from_browser: Optional[str] = typer.Option(None, help='Browser to get cookies from. '),
        output: str = typer.Option('.', help='Output path for downloaded videos.'),
        debug: bool = typer.Option(False, help='Enable debug mode. This disables headless mode of Browser.'),
        until_link: Optional[str] = typer.Option(
            None,
            help="Keeps finding videos until this link is found. None for no limit. Only for user's likes or media.",
        ),
        parallel: bool = typer.Option(False, help='Download videos in parallel.'),
):
    download_video(
        target_uris=target_uris,
        username=username,
        password=password,
        output=output,
        debug=debug,
        cookies_from_browser=cookies_from_browser,
        until_link=until_link,
        parallel=parallel,
    )
