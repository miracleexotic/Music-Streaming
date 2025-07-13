from textual import on, work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Grid, Horizontal
from textual.widgets import Button, Label

# Libs
from src.voice import Song, SongQueue
from src.ytdl import *


class ConfirmationScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(
        self,
        source: YTDLSource = None,
        insert_playlist=None,
        insert_song=None,
        songs: SongQueue = None,
        songs_listview=None,
    ) -> None:
        super().__init__()
        self.source = source
        self.insert_playlist = insert_playlist
        self.insert_song = insert_song
        self.songs = songs
        self.songs_listview = songs_listview

    def compose(self) -> ComposeResult:
        yield Grid(
            Horizontal(
                Label(f" 󰎇 ", classes="title --icon"),
                Label(f" {self.source.title} ", classes="title --content"),
            ),
            Horizontal(
                Label(f"", classes="duration --icon"),
                Label(f"{self.source.duration}", classes="duration --content"),
            ),
            Horizontal(
                Label(f"", classes="uploader --icon"),
                Label(f"{self.source.uploader}", classes="uploader --content"),
            ),
            Horizontal(
                Label(f"", classes="url --icon"),
                Label(f"{self.source.url}", classes="url --content"),
            ),
            Horizontal(
                Button(" Add", id="AddBtn"),
                Button(" Delete", id="DeleteBtn"),
            ),
            id="dialog",
        )

    @on(Button.Pressed, "#AddBtn")
    async def added(self) -> None:
        # Add to playlist table
        row_key = await self.insert_playlist(self.source)

        # Add to song listview
        await self.insert_song(self.source)

        # Add to songs queue
        song = Song(self.source, row_key)
        await self.songs.put(song)

        # Remove screen
        self.app.pop_screen()

    @on(Button.Pressed, "#DeleteBtn")
    async def deleted(self) -> None:
        # Remove song from songs listview
        self.songs_listview.remove_items((self.songs_listview.index,))

        # Remove screen
        self.app.pop_screen()
