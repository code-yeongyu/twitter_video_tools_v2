import os


class URIValidator:

    @staticmethod
    def is_twitter_link(link: str) -> bool:
        return link.startswith('https://twitter.com/')

    @staticmethod
    def is_media_link(link: str) -> bool:
        return link.endswith('/media')

    @staticmethod
    def is_liked_link(link: str) -> bool:
        return link.endswith('/likes')

    @staticmethod
    def is_monsnode_link(link: str) -> bool:
        return link.startswith('https://monsnode.com/')

    @staticmethod
    def is_file_path(path: str) -> bool:
        return os.path.isfile(path)
