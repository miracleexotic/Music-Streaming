from ytdl import *
import mpv
from datetime import datetime
from pprint import pprint
from threading import Thread


def logging(loglevel, component, message):
    # print(
    #     f'|{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}| [{loglevel}] {component}: {message}',
    #     end="",
    # )
    pass


def main():

    player_lst = []
    t_lst = []
    while True:
        command = input("> ")
        if command == "p" and len(player_lst) > 0:
            t_lst[0].start()
        elif command == "m":
            player_lst[0].keypress("m")
        elif command == "q":
            player = player_lst.pop()
            player.stop()
            del player
            player_lst.pop()
            t = t_lst.pop()
            del t
        else:
            search = input("search: ")

            player = mpv.MPV(
                log_handler=logging,
                ytdl=True,
                video=False,
                # terminal=True,
                # input_terminal=True,
                input_default_bindings=True,
            )
            player_lst.append(player)
            source = YTDLSource.create_source(search)

            t = Thread(target=play, args=(player, source.stream_url))
            t_lst.append(t)


def play(player, stream_url):
    player.play(stream_url)


if __name__ == "__main__":

    main()
