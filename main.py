from textual import on, work
from textual.app import App, ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.screen import Screen
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
    TabbedContent,
    TabPane,
    Rule,
    RichLog,
)
from textual.containers import Horizontal, Vertical

# Custom widgets and screen
from src.screen.confirmation import ConfirmationScreen
from src.screen.search import SearchScreen

# Libs
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

        self.songs_history: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="SearchBar"):
            yield Label("", id="SearchIcon")
            yield Input(placeholder="Search Music", id="SearchMusic")
            yield Button("Search", id="SearchBtn")
        with TabbedContent():
            with TabPane("Playlist", id="PlaylistTab"):
                yield DataTable(id="PlaylistTable")
            with TabPane("Songs", id="SongsTab"):
                yield ListView(id="SongsListView")

        #
        # Debuger
        #
        yield RichLog(id="debug")
        # self.query_one("#debug", RichLog).write(f"{event.item.id}")

        yield Footer()

    def on_mount(self) -> None:
        self.theme = "monokai"
        self.title = "Music"
        self.sub_title = "No Music for Playing"

        # Initial search input
        self.search_input = self.query_one("#SearchMusic", Input)

        # Initial playlist table
        self.playlist_table = self.query_one("#PlaylistTable", DataTable)
        self.playlist_table.cursor_type = "row"
        self.playlist_table.zebra_stripes = True
        self.playlist_table.add_columns("Title", "Duration")

        # Initial songs ListView
        self.songs_listview = self.query_one("#SongsListView", ListView)

    #
    # Search Music
    #
    @on(Input.Submitted, "#SearchMusic")
    @on(Button.Pressed, "#SearchBtn")
    async def submit_search(self) -> None:
        if self.search_input.value:
            await self.submit_get_source(self.search_input.value)
            if not self.voice_state.is_playing and not self.voice_state.audio_player:
                self.voice_state.audio_player = asyncio.get_event_loop().create_task(
                    self.voice_state.audio_player_task()
                )

            self.search_input.value = ""

    async def submit_get_source(self, search: str) -> None:
        entries = await YTDLSource.search_source(search)

        # Search Screen
        self.push_screen(
            SearchScreen(
                search=search,
                entries=entries,
                insert_playlist=self.insert_playlist,
                insert_song=self.insert_song,
                songs=self.voice_state.songs,
            )
        )

    #
    # Playlist Table
    #
    async def insert_playlist(self, source: YTDLSource) -> None:
        # Add to playlist table
        row_key = self.playlist_table.add_row(source.title, source.duration)

        return row_key

    @on(DataTable.RowSelected, "#PlaylistTable")
    async def playlist_table_selected(self) -> None:
        # Get the keys for the row and column under the cursor.
        row_key, _ = self.playlist_table.coordinate_to_cell_key(
            self.playlist_table.cursor_coordinate
        )
        if self.voice_state.current.row_key == row_key:
            return

        # Find song
        idx, song = self.voice_state.songs.find(row_key)
        self.voice_state.songs.remove(idx)
        self.voice_state.songs.add_first(song)

        # Play next song
        self.voice_state.player.stop()

    #
    # Songs ListView
    #
    async def insert_song(self, source: YTDLSource) -> None:
        # Add to songs history
        if source.url not in self.songs_history:
            self.songs_history.append(source.url)
            self.songs_listview.insert(
                0,
                (
                    ListItem(
                        Horizontal(
                            Label(f" 󰎇 ", classes="title --icon"),
                            Label(f" {source.title} ", classes="title --content"),
                        ),
                        Horizontal(
                            Label(f"", classes="duration --icon"),
                            Label(f"{source.duration}", classes="duration --content"),
                        ),
                        Horizontal(
                            Label(f"", classes="uploader --icon"),
                            Label(f"{source.uploader}", classes="uploader --content"),
                        ),
                        Horizontal(
                            Label(f"", classes="url --icon"),
                            Label(f"{source.url}", classes="url --content"),
                        ),
                        id=f"S{source.vid}",
                    ),
                ),
            )

    async def songs_get_source(self, search: str) -> None:
        source = await self.create_source(search)

        # Confirmation Screen
        self.push_screen(
            ConfirmationScreen(
                # Added
                source=source,
                insert_playlist=self.insert_playlist,
                insert_song=self.insert_song,
                songs=self.voice_state.songs,
                # Deleted
                songs_listview=self.songs_listview,
            )
        )

    @on(ListView.Selected, "#SongsListView")
    async def songs_listview_selected(self, event: ListView.Selected) -> None:
        search = f"https://www.youtube.com/watch?v={event.item.id[1:]}"
        await self.songs_get_source(search)

    #
    # YTDL Handler
    #
    async def create_source(self, search: str) -> YTDLSource:
        try:
            source = await YTDLSource.create_source(search)
            return source

        except YTDLError as e:
            # TODO: Implement logging
            pass

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
        # Clear Playlist table
        if self.voice_state.current:
            if self.playlist_table.row_count > 1:
                self.playlist_table.remove_row(self.voice_state.current.row_key)
            else:
                self.playlist_table.clear()

        # Trigger next song
        self.voice_state.next.set()

    @work(exclusive=True, thread=True)
    def action_player_skip(self):
        self.voice_state.player.stop()


if __name__ == "__main__":

    app = MusicApp()
    app.run()
