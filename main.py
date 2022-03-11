from moviepy.editor import *
from PIL import ImageColor
import requests
import json
from datetime import datetime


def generate_logo(__show__, __xpos__, __ypos__, __start__):
    if __show__['background_image'] != '':
        bg_logo_clip = ImageClip(__show__['background_image'])
        (w, h) = bg_logo_clip.size
        bg_logo_clip = bg_logo_clip.crop(width=LOGO_W, height=LOGO_H, x_center=w / 2, y_center=h / 2)
    else:
        bg_color_rgb = tuple(int(__show__['background_color'][i:i + 2], 16) for i in (0, 2, 4))
        bg_logo_clip = ColorClip(size=(LOGO_W, LOGO_H), color=bg_color_rgb)

    mask_clip = ImageClip("source/mask.png", ismask=True)

    logo_clip = ImageClip(__show__['logo_link'])
    logo_clip = logo_clip.resize(width=LOGO_W - 20)

    logo = CompositeVideoClip([bg_logo_clip.set_mask(mask_clip),
                               logo_clip.set_position("center")]) \
        .set_position((__xpos__, __ypos__)).set_start(__start__).set_duration(bg_duration - __start__).crossfadein(0.5)

    return logo


def generate_time_txt(__show__, __xpos__, __ypos__, __start__):
    time_clip = TextClip(__show__['inizio'], fontsize=50, color='white', font='Gotham-Light')

    time = CompositeVideoClip([time_clip]).set_position((__xpos__ + 150, __ypos__)).set_start(
        __start__).set_duration(bg_duration - __start__).crossfadein(0.5)

    return time


def generate_title_txt(__show__, __xpos__, __ypos__, __start__):
    title_clip = TextClip(__show__['nome'], fontsize=50, color='white', font='Gotham-Medium')

    title = CompositeVideoClip([title_clip]).set_position((__xpos__ + 330, __ypos__ - 1)).set_start(
        __start__).set_duration(bg_duration - __start__).crossfadein(0.5)

    return title


def get_day():
    days = ["LUNEDI'", "MARTEDI'", "MERCOLEDI'", "GIOVEDI'", "VENERDI'", "SABATO", "DOMENICA"]
    return days[datetime.today().weekday()]


# get from poliradio.it the list of shows of the day
response = requests.get("https://www.poliradio.it/api/todayShows.php")
show_list = json.loads(response.content)

# load the background video clip
bg_filename = "source/template.mp4"
bg_clip = VideoFileClip(bg_filename)

BG_W, BG_H = bg_clip.size
bg_duration = bg_clip.duration

LOGO_W = 120
LOGO_H = 120

SHOW_POS_Y = int(BG_H / 4) - 50
SHOW_POS_X = int(BG_W / 6)
START = 2.7

DAY = get_day()

day_txt_clip = TextClip(DAY, fontsize=70, color='white', font='Gotham-Bold').set_position(
    ('center', SHOW_POS_Y)).set_start(START)

layer_list = [bg_clip, day_txt_clip]

SHOW_POS_Y += 200

for show in show_list:
    layer_list.append(generate_logo(show, SHOW_POS_X, SHOW_POS_Y, START))
    SHOW_POS_Y += 40
    layer_list.append(generate_time_txt(show, SHOW_POS_X, SHOW_POS_Y, START))
    layer_list.append(generate_title_txt(show, SHOW_POS_X, SHOW_POS_Y, START))
    SHOW_POS_Y += 150
    START += 0.2

final = CompositeVideoClip(layer_list)

final.set_duration(bg_duration).write_videofile("out.mp4")
