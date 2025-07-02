import asyncio
import yt_dlp


class YTDLError(Exception):
    pass


class YTDLSource:
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

    def __init__(self, data) -> None:
        self.data = data

        self.uploader = data.get("uploader") or ""
        self.uploader_url = data.get("uploader_url") or ""
        date = data.get("upload_date") or ""
        self.upload_date = date[6:8] + "." + date[4:6] + "." + date[0:4] or ""
        self.title = data.get("title") or ""
        self.thumbnail = data.get("thumbnail") or ""
        self.description = data.get("description") or ""
        self.duration = self.parse_duration(
            int(data.get("duration")) if data.get("duration") else 0
        )
        self.tags = data.get("tags") or ""
        self.url = data.get("webpage_url") or ""
        self.views = data.get("view_count") or ""
        self.likes = data.get("like_count") or ""
        self.dislikes = data.get("dislike_count") or ""
        self.stream_url = data.get("url") or ""

    @classmethod
    def create_source(cls, search: str):
        if not search.startswith("https://www.youtube.com"):
            search = f"ytsearch:{search}"

        print(f"[+] Search: {search}")
        search_data = cls.ytdl.extract_info(
            search,
            download=False,
            process=False,
        )

        if search_data is None:
            raise YTDLError(f"Couldn't find anything that matches `{search}`")

        search_info = cls.get_info(search_data)

        # Search with youtube url with provide 'webpage_url'
        if "webpage_url" in search_info:
            url = search_info["webpage_url"]

        # Search with key word provide 'url'
        if "url" in search_info:
            url = search_info["url"]

        print(f"[+] URL: {url}")
        processed_data = cls.ytdl.extract_info(url, download=False)

        if processed_data is None:
            raise YTDLError(f"Couldn't fetch `{url}`")

        info = cls.get_info(processed_data)

        return cls(data=info)

    @staticmethod
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

    @staticmethod
    def parse_duration(duration: int):
        if duration > 0:
            minutes, seconds = divmod(duration, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)

            duration = []
            if days > 0:
                duration.append(f"{days}")
            if hours > 0:
                duration.append(f"{hours}")
            if minutes > 0:
                duration.append(f"{minutes}")
            if seconds > 0:
                duration.append(f"{seconds}")

            value = ":".join(duration)

        elif duration == 0:
            value = "LIVE"

        return value


if __name__ == "__main__":

    # search = "fml"
    # search = "https://www.youtube.com/watch?v=Dcx9R4QSeik"

    search = input("> ")
    source = YTDLSource.create_source(search)
    print(f"Stream Url: {source.stream_url}")
