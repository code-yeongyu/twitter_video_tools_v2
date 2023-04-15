from __future__ import annotations

import typing

import httpx
from bs4 import BeautifulSoup


class MonsnodeParser:
    TARGET_URL = 'https://monsnode.com/'
    timeout: float = 5

    def is_target_reachable(self) -> bool:
        try:
            httpx.get(self.TARGET_URL, timeout=self.timeout)
            return True
        except httpx.TimeoutException:
            return False

    def get_video(self, link: str) -> tuple[str, str]:
        request = httpx.get(link, timeout=self.timeout)
        soup = BeautifulSoup(request.text, 'html.parser')

        video_name = self._parse_video_name(soup)
        link = self._parse_video_url(soup)

        return video_name, link

    def _parse_video_name(self, soup: BeautifulSoup) -> str:
        uploader_name = soup.select('body > div:nth-child(2) > div:nth-child(2) > div:nth-child(5) > b')[0].text
        title = soup.select('body > div:nth-child(2) > div:nth-child(2) > div:nth-child(2)')[0].text
        title = title.replace('/', '_')
        title = title.replace('\n', '')
        return f'{uploader_name} - {title}.mp4'

    def _parse_video_url(self, soup: BeautifulSoup) -> str:
        video_path = typing.cast(
            str,
            soup.select('body > div:nth-child(2) > div:nth-child(1) > a:nth-child(2)')[0]['href'],
        )
        return self.TARGET_URL + video_path
