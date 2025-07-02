import asyncio
import yt_dlp


class YTDLError(Exception):
    pass


YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "extractaudio": True,
    "audioformat": "mp3",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
    # "proxy": "http://tor-proxy:8118",
}


ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


def ytdl_get_stream_info(search: str) -> str:
    if not search.startswith("https://www.youtube.com"):
        search = f"ytsearch:{search}"

    print(f"[+] Search: {search}")
    data = ytdl.extract_info(
        search,
        download=False,
        process=False,
    )

    if data is None:
        raise YTDLError(f"Couldn't find anything that matches `{search}`")

    search_info = get_info(data)

    # Search with youtube url with provide 'webpage_url'
    if "webpage_url" in search_info:
        url = search_info["webpage_url"]

    # Search with key word provide 'url'
    if "url" in search_info:
        url = search_info["url"]

    print(f"[+] URL: {url}")
    processed_info = ytdl.extract_info(url, download=False)

    if processed_info is None:
        raise YTDLError(f"Couldn't fetch `{url}`")

    info = get_info(processed_info)

    return info


def get_info(data):
    if "entries" not in data:
        # Specific entry to process.
        # eg. search with youtube
        # url: https://www.youtube.com/watch?v=Dcx9R4QSeik"
        info = data
    else:
        # Need to select some entry from search.
        # eg. search with key word.
        info = None
        for entry in data["entries"]:
            if entry:
                info = entry
                break

        if info is None:
            raise YTDLError(
                f"Couldn't find/retrieve anything that matches for `{data['id']}`"
            )

    return info


if __name__ == "__main__":

    # search = "fml"
    search = "https://www.youtube.com/watch?v=Dcx9R4QSeik"

    stream_info = ytdl_get_stream_info(search)
    print(f"Stream Url: {stream_info['url']}")
