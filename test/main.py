from textual import on, work
from textual.app import App, ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Header, Input, Label, Static

import asyncio
from ytdl import *
import mpv
import voice


class MusicApp(App):

    def __init__(self):
        super().__init__()
        self.player = mpv.MPV(
            ytdl=True,
            video=False,
            input_default_bindings=True,
        )
        self.voice_state = voice.VoiceState(self.player)
        self.player_observe_property()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Search Music", id="SearchMusic")
        yield Static("StreamUrl", id="StreamUrl")

    def on_mount(self) -> None:
        self.theme = "tokyo-night"
        self.title = "Music"
        self.sub_title = "No Music for Playing"

    @on(Input.Submitted, "#SearchMusic")
    async def submit_search(self) -> None:
        search_input = self.query_one("#SearchMusic", Input)
        if search_input.value:
            await self.get_source(search_input)
            if not self.voice_state.is_playing:
                del self.voice_state.audio_player
                self.voice_state.audio_player = asyncio.get_event_loop().create_task(
                    self.voice_state.audio_player_task()
                )

    async def get_source(self, search_input: Input) -> None:
        source = await YTDLSource.create_source(search_input.value)
        self.query_one("#StreamUrl", Static).update(source.title)
        search_input.value = ""
        await self.voice_state.songs.put(voice.Song(source))

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

            self.voice_state.next.set()

    def parse_duration(self, duration: int):
        minutes, seconds = divmod(duration, 60)

        duration = []
        duration.append(f"{minutes}")
        duration.append(f"{seconds}")

        value = ":".join(duration)
        return value


if __name__ == "__main__":

    app = MusicApp()
    app.run()
