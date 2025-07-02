import asyncio
import random
import logging
import multiprocessing

import ytdl
import mpv


PLAYER_TIMEOUT = 600  # 10 min

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("./logs/voice.log")
file_handler.setLevel(logging.NOTSET)
file_format = logging.Formatter(
    "[%(asctime)s] %(funcName)-20s :: %(levelname)-8s :: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
file_handler.setFormatter(file_format)

logger.addHandler(file_handler)


class Song:
    def __init__(self, source: ytdl.YTDLSource, row_key: str):
        self.source = source
        self.row_key = row_key


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, player: mpv.MPV):
        logger.debug("VoiceState")
        self.current: Song | None = None
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.exists = True

        # Audio player
        self.audio_player = None
        self.player: mpv.MPV = player
        self.command: multiprocessing.Queue = multiprocessing.Queue()

    @property
    def is_playing(self):
        return bool(self.current)

    async def getCurrentSong(self):
        """
        Get current song from queue.
        """

        logger.debug("Waiting for getting song...")
        self.current = await self.songs.get()
        logger.info(f'[i] Song: {str(self.current.source.title).encode("utf-8")}')
        return True

    async def playCurrentSong(self):
        """Play current song."""

        logger.info("[+] Starting")
        # def mpv_worker(song: Song, command: multiprocessing.Queue):
        #     player = mpv.MPV(
        #         ytdl=True,
        #         video=False,
        #         input_default_bindings=True,
        #     )
        #     player.play(song.source.stream_url)
        #
        #     while not player.idle_active:
        #         cmd = command.get()
        #         if cmd == "pause/resume":
        #             player.pause = not player.pause
        #         elif cmd == "skip":
        #             player.terminate()
        #             break
        #
        #     self.next.set()
        #
        # p = multiprocessing.Process(
        #     target=mpv_worker, args=(self.current, self.command)
        # )
        # p.start()
        self.player.play(self.current.source.stream_url)
        logger.info("[+] Playing song...")

    async def play_source(self):
        """Play song in queue."""

        try:
            async with asyncio.timeout(PLAYER_TIMEOUT):
                ok = await self.getCurrentSong()
                if not ok:
                    return False

        except asyncio.TimeoutError:
            logger.error("[!] Timeout")
            raise TimeoutError

        await self.playCurrentSong()
        return True

    async def audio_player_task(self):
        """Audio player."""

        logger.debug("--- Start Audio Player ---")

        while True:

            # clear now source
            self.next.clear()
            logger.debug(f"Queue: {self.songs.maxsize}")

            # exists
            if not self.exists:
                logger.debug("--- Stop Audio Player ---")
                return

            try:
                logger.debug("MODE: SOURCE")
                ok = await self.play_source()
                if not ok:
                    continue

            except TimeoutError:
                self.exists = False
                return

            await self.next.wait()
