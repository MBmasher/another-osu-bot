import re
import json
import requests
import sys
import configparser
import math
import calc
import beatmap
import diff_calc
import pp_calc
import time
from datetime import datetime, timezone

def get_date(record):
    return datetime.strptime(record[12][1], '%Y-%m-%d %H:%M:%S')

def return_recent(user, best, number, last_beatmap):
    if user == [0]:
        return 5, 0, 0, 0, 0, 0, 0, 0

    try:
        f = open('keys.cfg');
        config = configparser.ConfigParser()
        config.readfp(f)
        key = config._sections["osu"]['api_key']
    except:
        raise Exception("Invalid config")

    index_adjust = 0
    date_index_adjust = 0

    url = 'https://osu.ppy.sh/api/get_user_recent?k={}&u={}&limit=50'.format(key, user)
    if best == 1 or best == 3:
        url = 'https://osu.ppy.sh/api/get_user_best?k={}&u={}&limit=100'.format(key, user)
    if best == 2:
        url = 'https://osu.ppy.sh/api/get_scores?k={}&u={}&b={}&limit=100'.format(key, user, last_beatmap)
        index_adjust = 1
        date_index_adjust = 1
    jsonurl = str(requests.get(url).text)
    jsonurl = jsonurl[1:-2]
    user_split = [i[1:] for i in jsonurl.split("},")]
    play_info = []
    for i in range(len(user_split)):
        play_info.append([])
        info_list = user_split[i].split(",")
        play_info[i] = [(x.split(":")[0][1:-1], ":".join(x.split(":")[1:])[1:-1]) for x in info_list]

    if number > len(play_info):
        return play_info, user, 0, 0, 0, 0, 0, 0

    if len(play_info[0]) <= 1:
        return play_info, user, 0, 0, 0, 0, 0, 0

    if best == 3:
        play_info = sorted(play_info, key=get_date, reverse=True)


    datetime_rb = datetime.strptime(play_info[number-1][12+date_index_adjust][1], '%Y-%m-%d %H:%M:%S')
    now = int(time.time())
    d = divmod(now - datetime_rb.replace(tzinfo=timezone.utc).timestamp(), 86400)  # days
    h = divmod(d[1], 3600)  # hours
    m = divmod(h[1], 60)  # minutes
    s = m[1]  # seconds
    if d[0] > 0:
        if int(d[0]) == 1:
            time_ago = "1 day ago"
        else:
            time_ago = "{} days ago".format(int(d[0]))
    elif h[0] > 0:
        if int(h[0]) == 1:
            time_ago = "1 hour ago"
        else:
            time_ago = "{} hours ago".format(int(h[0]))
    elif m[0] > 0:
        if int(m[0]) == 1:
            time_ago = "1 minute ago"
        else:
            time_ago = "{} minutes ago".format(int(m[0]))
    else:
        if int(s) == 1:
            time_ago = "1 second ago"
        else:
            time_ago = "{} seconds ago".format(int(s))

    print(play_info)

    if best != 2:
        b_id = play_info[number-1][0][1]
    else:
        b_id = last_beatmap

    mods = int(play_info[number-1][10+index_adjust][1])
    time_multiplier = 1
    mods_string = ""
    if mods & 0b1: mods_string += "NF"
    if mods & 0b1 << 11: mods_string += "SO"
    if mods & 0b1 << 1: mods_string += "EZ"
    if mods & 0b1 << 8:
        time_multiplier = 0.75
        mods_string += "HT"
    if mods & 0b1 << 3: mods_string += "HD"
    if mods & 0b1 << 9:
        time_multiplier = 1.5
        mods_string += "NC"
    elif mods & 0b1 << 6:
        time_multiplier = 1.5
        mods_string += "DT"
    if mods & 0b1 << 4: mods_string += "HR"
    if mods & 0b1 << 10: mods_string += "FL"
    if mods & 0b1 << 14:
        mods_string += "PF"
    elif mods & 0b1 << 5:
        mods_string += "SD"

    if mods_string == "":
        mods_string = "None"

    new_beatmap = calc.return_beatmap(mods_string, b_id)

    diff_file = diff_calc.main(new_beatmap)

    combo = play_info[number-1][2+index_adjust][1]
    c50 = play_info[number-1][3+index_adjust][1]
    c100 = play_info[number-1][4+index_adjust][1]
    c300 = play_info[number-1][5+index_adjust][1]
    misses = play_info[number-1][6+index_adjust][1]
    pp = calc.return_values(c100, c50, misses, combo, str(b_id), mods_string)
    max_pp = calc.return_values("", "", "", "", str(b_id), mods_string)

    objects = len(new_beatmap.objects)

    url = 'https://osu.ppy.sh/api/get_beatmaps?k={}&b={}'.format(key, b_id)
    jsonurl = str(requests.get(url).text)
    jsonurl = jsonurl[2:-2]
    beatmap_split = jsonurl.split(",")
    beatmap_info = [(x.split(":")[0][1:-1], ":".join(x.split(":")[1:])[1:-1]) for x in beatmap_split]

    song_length = int(int(beatmap_info[3][1])/time_multiplier)
    drain_length = int(int(beatmap_info[4][1])/time_multiplier)
    diff = beatmap_info[5][1]
    cs = new_beatmap.cs
    od = new_beatmap.od
    ar = new_beatmap.ar
    hp = new_beatmap.hp
    artist = beatmap_info[14][1]
    song_title = beatmap_info[15][1]
    mapper = beatmap_info[16][1]
    bpm = int(int(beatmap_info[18][1])*time_multiplier)
    max_combo = beatmap_info[26][1]
    star_rating = diff_file[2]

    status_num = int(beatmap_info[2][1])
    if status_num == 1:
        status_s = "Ranked"
    elif status_num == 2:
        status_s = "Approved"
    elif status_num == 3:
        status_s = "Qualified"
    elif status_num == 4:
        status_s = "Loved"
    else:
        status_s = "the fuck?"

    song_min = math.floor(song_length/60)
    song_sec = song_length % 60
    drain_min = math.floor(drain_length/60)
    drain_sec = drain_length % 60

    song_length = "{:02d}:{:02d}".format(song_min, song_sec)
    drain_length = "{:02d}:{:02d}".format(drain_min, drain_sec)

    title = "{} - {} ({}) [{}]".format(artist,
                                       song_title,
                                       mapper,
                                       diff)
    link = 'https://osu.ppy.sh/b/{}'.format(beatmap_info[1][1])

    map_text_list = [
        "__**Map Information:**__",
        "**Stars:** {:.2f}*".format(star_rating),
        "**Difficulty Settings:** CS{:.1f} | AR{:.1f} | OD{:.1f} | HP{:.1f}".format(cs, ar, od, hp),
        "**Song Settings:** {} BPM | length {} (drain {})".format(bpm, song_length, drain_length),
        "**Status:** {}".format(status_s)
    ]

    map_text = '\n'.join(map_text_list)

    url = 'https://osu.ppy.sh/api/get_user?k={}&u={}'.format(key, user)
    jsonurl = str(requests.get(url).text)
    jsonurl = jsonurl[2:-2]
    user_split = jsonurl.split(",")
    user_info = [(x.split(":")[0][1:-1], ":".join(x.split(":")[1:])[1:-1]) for x in user_split]

    username = user_info[1][1]
    rank = user_info[9][1]
    pp_total = user_info[11][1]
    country = user_info[18][1]
    country_rank = user_info[20][1]

    user_info_s = "{} | {}pp, global #{} ({} #{})".format(username, pp_total, rank, country, country_rank)
    user_link = "https://osu.ppy.sh/u/{}".format(user)

    user_pfp = "https://a.ppy.sh/{}".format(user)

    score = play_info[number-1][1][1]
    grade = play_info[number-1][13+index_adjust][1]

    if grade == "F":
        grade += " ({:.2f}% completion)".format(100 * ((int(c50) + int(c100) + int(c300) + int(misses)) / objects))

    fc_string = ""

    if int(combo) < int(max_combo):
        fc_pp = calc.return_values(c100, c50, 0, max_combo, str(b_id), mods_string)
        fc_string = " FC {:.2f}pp /".format(fc_pp.pp)

    final_pp = pp.pp

    if best:
        final_pp = float(play_info[number-1][14+index_adjust][1])

    url = 'https://osu.ppy.sh/api/get_scores?k={}&b={}&limit=100'.format(key, b_id)
    jsonurl = str(requests.get(url).text)
    jsonurl = jsonurl[1:-2]
    user_split = [i[1:] for i in jsonurl.split("},")]
    leaderboard_info = []
    for i in range(len(user_split)):
        leaderboard_info.append([])
        info_list = user_split[i].split(",")
        leaderboard_info[i] = [(x.split(":")[0][1:-1], ":".join(x.split(":")[1:])[1:-1]) for x in info_list]

    rank_string = ""
    for i in range(100):
        if leaderboard_info[i][1][1] == str(score) and leaderboard_info[i][2][1] == username:
            rank_string = " __**#{}**__".format(i+1)
            break

    url = 'https://osu.ppy.sh/api/get_user_best?k={}&u={}&limit=100'.format(key, user)
    jsonurl = str(requests.get(url).text)
    jsonurl = jsonurl[1:-2]
    user_split = [i[1:] for i in jsonurl.split("},")]
    top_scores_info = []
    for i in range(len(user_split)):
        top_scores_info.append([])
        info_list = user_split[i].split(",")
        top_scores_info[i] = [(x.split(":")[0][1:-1], ":".join(x.split(":")[1:])[1:-1]) for x in info_list]

    top_score_string = ""
    for i in range(100):
        if top_scores_info[i][1][1] == str(score) and top_scores_info[i][0][1] == str(b_id):
            top_score_string = " __**#{}**__".format(i + 1)
            break

    play_info_list = [
        "__**Play Information:**__",
        "**Grade:** {}".format(grade),
        "**Mods:** {}".format(mods_string),
        "**Score:** {}{}".format(score, rank_string),
        "**Accuracy:** {:.2f}%".format(100 * (int(c300)*3 + int(c50)*0.5 + int(c100))/((int(c300)+int(c100)+int(c50)+int(misses))*3)),
        "**Hits:** {} / {} / {} / {}".format(c300, c100, c50, misses),
        "**Combo:** {}/{}x".format(combo, max_combo),
        "**Performance:** __{:.2f}pp__{} /{} SS {:.2f}pp".format(final_pp, top_score_string, fc_string, max_pp.pp),
        "**When:** {}".format(time_ago),
    ]

    if best == 0:
        tries = 0
        for i in range(49):
            if i < number:
                continue
            if play_info[i][0][1] == str(b_id) and play_info[i][10][1] == str(mods):
                tries += 1
            else:
                break
        if tries >= 49:
            play_info_list.append("**Try:** 49+")
        else:
            play_info_list.append("**Try:** {}".format(tries))

    play_info_s = '\n'.join(play_info_list)

    difficulty_settings = play_info_s + '\n\n' + map_text

    return play_info, title, link, difficulty_settings, user_info_s, user_link, user_pfp, b_id