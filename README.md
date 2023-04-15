# Twitter Video Tools V2

- A Twitter video downloader
- supports downloading videos from twitter (or specific user from twitter) && monsnode.

## Install

### with PIP

```sh
pip install twtvt
```

### with Poetry

```sh
poetry add twtvt
```

## Usage

### Command line

```sh
twtvt --help
```

Supported link types:

- Video tweet: <https://twitter.com/twtvtOfficial/status/1599748329927499777>
- Video from [monsnode](https://monsnode.com): <https://monsnode.com/v1506575871309589251>
- Specific user's uploaded videos: <https://twitter.com/twtvtOfficial/media>
- Specific user's liked videos: <https://twitter.com/twtvtOfficial/likes>

### Python Embedding

```python
import twtvt

twtvt.download_video(
    target_links=['https://twitter.com/twtvtOfficial/media', 'https://monsnode.com/v1506575871309589251'],
    username='your username',
    password='your password',
    output='./videos',
    cookies_from_browser='brave',
    until_link='https://twitter.com/twtvtOfficial/status/1599748329927499777',
)
```
