class URLValidator:
    link: str

    def __init__(self, link: str) -> None:
        self.link = link

    def is_valid_twitter_media_link(self) -> bool:
        return self.is_valid_link() and self._is_twitter_media_link()

    def is_valid_twitter_liked_link(self) -> bool:
        return self.is_valid_link() and self._is_twitter_liked_link()

    def is_valid_link(self) -> bool:
        return self.link.startswith('https://twitter.com/') or self.link.startswith('https://monsnode.com/')

    def _is_twitter_media_link(self) -> bool:
        return self.link.endswith('/media')

    def _is_twitter_liked_link(self) -> bool:
        return self.link.endswith('/likes')
