#!/usr/bin/env python3
import multiprocessing
import mpv
import time
import concurrent.futures


s = "https://rr5---sn-5fo-c33l7.googlevideo.com/videoplayback?expire=1751404778&ei=ivxjaPqDMeeo9fwPkoTfqQU&ip=49.229.199.70&id=o-AFpocr2p-QFabgNx7wO4N1YsU3YoA2f1YWVXBKSu2aiy&itag=251&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1751383178%2C&mh=HI&mm=31%2C26&mn=sn-5fo-c33l7%2Csn-npoe7nsr&ms=au%2Conr&mv=m&mvi=5&pcm2cms=yes&pl=22&rms=au%2Cau&gcr=th&initcwndbps=385000&bui=AY1jyLOAZJP9ufI_CCSt9NwB41vBxHMGAYwB4nY02BIzut1dNaSmtSwXi5kfLsrJGB0gfQRdyOYG0kfl&vprv=1&svpuc=1&mime=audio%2Fwebm&ns=s8tDEZYWdpyMJJNkpBQK2zMQ&rqh=1&gir=yes&clen=3589030&dur=223.341&lmt=1729116974486549&mt=1751382781&fvip=1&keepalive=yes&lmw=1&c=TVHTML5&sefc=1&txp=5532434&n=6q0bFFr2SUEf4w&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cgcr%2Cbui%2Cvprv%2Csvpuc%2Cmime%2Cns%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpcm2cms%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRQIgRoxIoAnfgF61MWYtMeufrHwFovNx2jA4jPs4BlmMIWgCIQCCdTPBsWvg7wvzbg5_1iVbpcwqh9Kz856TeBcqPdFaxQ%3D%3D&sig=AJfQdSswRQIhALjWYgwqdKDKxAifHpuTMY0cKuvvfRKqt8OGGayxh6fxAiANBMUFH2R7cf5RcEIhQQDqSZdoc0IQPxiF-oG_jeV2kQ%3D%3D"
player = mpv.MPV(
    video=False,
    ytdl=True,
    input_default_bindings=True,
    terminal=True,
    input_terminal=True,
)
player.play(s)
player.wait_for_playback()


def mpv_worker(s, command):
    player = mpv.MPV(video=False, ytdl=True, input_default_bindings=True, terminal=True)
    player.play(s)

    while (not player.idle_active) or (not player.pause):
        cmd = command.get()
        if cmd == "p":
            print(f"{cmd}: {player.pause}")
            player.pause = not player.pause

    # player.wait_for_playback()


# command = multiprocessing.Queue()
#
# p = multiprocessing.Process(target=mpv_worker, args=(s, command), daemon=True)
# p.start()
#
# with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
#     futures = {executor.submit(mpv_worker, s=s)}
#     concurrent.futures.as_completed(futures)

# while True:
#     cmd = input("> ")
#     if cmd == "q":
#         break
#
#     command.put(cmd)
