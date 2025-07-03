from textual import on, work
from textual.app import App, ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Static,
    DataTable,
    DataTable,
    ListItem,
    ListView,
)
from textual.containers import Horizontal, Vertical

import asyncio
import mpv
from src.ytdl import *
import src.voice as voice


class MusicApp(App):

    CSS_PATH = "styles.scss"

    BINDINGS = [
        ("ctrl+z", "player_skip", "Skip music"),
    ]

    def __init__(self):
        super().__init__()
        self.player = mpv.MPV(
            ytdl=True,
            video=False,
            input_default_bindings=True,
        )
        self.player_observe_property()
        self.voice_state = voice.VoiceState(self.player)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="SearchBar"):
            yield Label("", id="SearchIcon")
            yield Input(placeholder="Search Music", id="SearchMusic")
            yield Button("Search", id="SearchBtn")
        # yield Label("DEBUG", id="debug")
        yield DataTable(id="SongList")
        yield Footer()

    def on_mount(self) -> None:
        self.theme = "monokai"
        self.title = "Music"
        self.sub_title = "No Music for Playing"

        self.songList_table = self.query_one("#SongList", DataTable)
        self.songList_table.cursor_type = "row"
        self.songList_table.zebra_stripes = True
        self.songList_table.add_columns("Title", "Duration", "Uploader", "URL")

    #
    # Search Music
    #
    @on(Input.Submitted, "#SearchMusic")
    async def submit_search(self) -> None:
        search_input = self.query_one("#SearchMusic", Input)
        if search_input.value:
            await self.get_source(search_input)
            if not self.voice_state.is_playing and not self.voice_state.audio_player:
                self.voice_state.audio_player = asyncio.get_event_loop().create_task(
                    self.voice_state.audio_player_task()
                )

    async def get_source(self, search_input: Input) -> None:
        source = await YTDLSource.create_source(search_input.value)
        row_key = self.songList_table.add_row(
            source.title, source.duration, source.uploader, source.url
        )
        search_input.value = ""
        await self.voice_state.songs.put(voice.Song(source, row_key))
        # self.query_one("#debug", Static).update(
        #     f"{source.title}:{len(self.voice_state.songs)}"
        # )

    #
    # Sougs Queue
    #

    #
    # MPV Handler
    #
    def player_observe_property(self):
        self.player.observe_property(
            "time-pos", lambda name, value: self.update_time_observer(name, value)
        )
        self.player.observe_property(
            "idle-active", lambda name, value: self.update_time_end(name, value)
        )

    @work(exclusive=True, thread=True)
    def update_time_observer(self, _name, value):
        if value:
            self.title = f"{self.voice_state.current.source.title}"
            self.sub_title = f"Now playing at {self.parse_duration(int(value))}/{self.voice_state.current.source.duration}"

    @work(exclusive=True, thread=True)
    def update_time_end(self, _name, value):
        if value:
            self.title = "Music"
            self.sub_title = "No Music for Playing"

            self.play_next_song()

    def parse_duration(self, duration: int):
        minutes, seconds = divmod(duration, 60)

        duration = []
        duration.append(f"{minutes}")
        duration.append(f"{seconds}")

        value = ":".join(duration)
        return value

    def play_next_song(self):
        # Clear Song list table
        if self.voice_state.current:
            if self.songList_table.row_count > 1:
                self.songList_table.remove_row(self.voice_state.current.row_key)
            else:
                self.songList_table.clear()

        # Trigger next song
        self.voice_state.next.set()

    @work(exclusive=True, thread=True)
    def action_player_skip(self):
        self.voice_state.player.stop()


if __name__ == "__main__":

    app = MusicApp()
    app.run()
