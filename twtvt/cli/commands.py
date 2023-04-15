from typing import Optional

import typer
from typer import Typer

cli_app = Typer()


@cli_app.command()
def twtvt(
        link: str = typer.Argument(..., help="Video tweet link or target user's likes or media."),
        username: Optional[str] = typer.Option(None, help='Your twitter credentials username.'),
        password: Optional[str] = typer.Option(None, help='Your twitter credentials password.'),
        until_link: Optional[str] = typer.Option(
            None,
            help="Keeps finding videos until this link is found. None for no limit. Only for user's likes or media.",
        ),
        output: str = typer.Option('videos', help='Output path for downloaded videos.'),
        debug: bool = typer.Option(False, help='Enable debug mode. This disables headless mode of Browser.'),
):
    pass
