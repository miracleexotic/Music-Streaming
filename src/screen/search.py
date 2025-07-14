from textual import on, work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import ListView, ListItem
from textual.containers import Grid, Horizontal
from textual.widgets import Button, Label

# Libs
from src.voice import Song, SongQueue
from src.ytdl import *


class SearchScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(
        self,
        search: str = None,
        entries: list = None,
        insert_playlist=None,
        insert_song=None,
        songs: SongQueue = None,
    ) -> None:
        super().__init__()
        self.search = search
        self.entries = entries
        self.insert_playlist = insert_playlist
        self.insert_song = insert_song
        self.songs = songs

    def compose(self) -> ComposeResult:
        listitems = []
        for entry in self.entries:
            listitems.append(
                ListItem(
                    Horizontal(
                        Label(f" 󰎇 ", classes="title --icon"),
                        Label(f" {entry.get('title')} ", classes="title --content"),
                    ),
                    Horizontal(
                        Label(f"", classes="duration --icon"),
                        Label(
                            f"{YTDLSource.parse_duration(int(entry.get('duration')))}",
                            classes="duration --content",
                        ),
                    ),
                    Horizontal(
                        Label(f"", classes="uploader --icon"),
                        Label(f"{entry.get('uploader')}", classes="uploader --content"),
                    ),
                    Horizontal(
                        Label(f"", classes="url --icon"),
                        Label(f"{entry.get('url')}", classes="url --content"),
                    ),
                    id=f"S{entry.get('url').split('https://www.youtube.com/watch?v=')[1]}",
                ),
            )

        yield Grid(ListView(*listitems, id="SearchListView"), id="dialog")

    @on(ListView.Selected, "#SearchListView")
    async def added(self, event: ListView.Selected) -> None:
        source = await YTDLSource.create_source(
            f"https://www.youtube.com/watch?v={event.item.id[1:]}"
        )

        # Add to playlist table
        row_key = await self.insert_playlist(source)

        # Add to song listview
        await self.insert_song(source)

        # Add to songs queue
        song = Song(source, row_key)
        await self.songs.put(song)

        # Remove screen
        self.app.pop_screen()
