# A Simple Telegram Bot, which will send you current playing song's lyrics from spotify to telegram

# Copyright(C) 2021-Present Gautam Kumar < https://github.com/gautamajay52 >

import html
import os
import re


from lyricsgenius import Genius
from tekore import Spotify, refresh_user_token
from tekore._sender import client

genius_token = os.environ.get("GENIUS")

genius = Genius(genius_token)


class mySpotify(Spotify):
    def __init__(self, client_id, client_secret, refresh_token):
        self.token = refresh_user_token(
            client_id, client_secret, refresh_token)
        self.artist = ""
        self.song_name = ""
        self.title = ""
        super().__init__(self.token)

    def __get_current_song(self):
        return self.playback_currently_playing()

    def __get_song_artist(self):
        current = self.__get_current_song()
        if current:
            self.artist = [art.name for art in current.item.album.artists]
            self.song_name = current.item.name

    def __get_lyrics(self):
        if not self.song_name and self.artist:
            return
        song_to_search = self.song_name.split("(")[0].strip()  # why-tf
        song = genius.search_song(title=song_to_search, artist=self.artist[0])
        if song:
            lyrics = song.lyrics
            # fix for error https://github.com/johnwmillr/LyricsGenius/pull/215
            lyrics = lyrics.replace("EmbedShare Url:CopyEmbed:Copy", "")
            return lyrics

    def my_song_title(self):
        self.__get_song_artist()
        if self.song_name and self.artist:
            artist = ", ".join([a for a in self.artist])
            self.title = f"{self.song_name} by {artist}"
            return self.title

    def parse_lyrics(self):
        lyrics = self.__get_lyrics()
        if not lyrics:
            return
        lyrics = html.escape(lyrics)
        lyrics = re.sub(r"(.+)", self.beautifier, lyrics)
        lyrics = f"<br>=============== gautamajay52 ===============<br>🔊 <b>{self.title}</b>{lyrics}<br>=============== gautamajay52 ===============" # to-do ;)
        return lyrics

    # not tested (all premium features)
    def pause_song(self):
        return self.playback_pause()

    def next_song(self):
        return self.playback_next()

    def resume_song(self):
        return self.playback_resume()

    def prev_song(self):
        return self.playback_previous()

    @staticmethod
    def beautifier(t):
        lyrics = "<br>"
        if t.group(0).startswith("["):
            lyrics += f"<br><b>🎶  {t.group(0)}  🎶</b>"
        else:
            lyrics += f"{t.group(0)}"
        return lyrics
