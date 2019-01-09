import discord
import recent
import random
import os
import time
import asyncio
import sys
from datetime import datetime, timezone

class Periodic:
    def __init__(self, func, time):
        self.func = func
        self.time = time
        self.is_started = False
        self._task = None

    async def start(self):
        if not self.is_started:
            self.is_started = True
            # Start task to call func periodically:
            self._task = asyncio.ensure_future(self._run())

    async def stop(self):
        if self.is_started:
            self.is_started = False
            # Stop task and await it stopped:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self):
        while True:
            await asyncio.sleep(self.time)
            self.func()

client = discord.Client()

key = os.environ.get('API_KEY')
TOKEN = os.environ.get('TOKEN')

spectating_users = []
low_detail_spectating_users = []

fin = open('keys.cfg', 'r+')
fin.truncate(0)
fin.seek(0)
fin.write("[osu]\napi_key = {}".format(key))
fin.close()

logging_message = None
last_api_log_time = time.time()
on_time = time.time()

if client.get_channel("530513525429370893") is None:
    logging = False
    logging_channel = None
else:
    logging = True
    logging_channel = client.get_channel("530513525429370893")

rolling = False
roll_number = 0
rolling_channel = None

api_in_last_logged = 0
api_peak = 0

last_beatmap = 0

async def spectate_recent():
    global spectating_users, api_in_last_logged, logging_channel

    try:
        new_list = []

        for message, user, time_ in spectating_users:
            if (time.time() > time_ + 3600):
                await client.edit_message(message, "Timeout (1 hour): Stopped spectating {}.".format(user))
            else:
                new_list.append((message, user, time_))
                play_list, title_s, link_s, diff_s, user_info_s, user_link, user_pfp, b_id, s_id = recent.return_recent(
                    user, 0, 1, 0, False)
                if play_list != 5:
                    if len(play_list[0]) <= 1:
                        await client.edit_message(message, "Spectating {}...\n{} has no recent plays!".format(user, user))
                    else:
                        emb = discord.Embed(title=title_s, description=diff_s, url=link_s)
                        emb.set_author(name=user_info_s, url=user_link, icon_url=user_pfp)
                        emb.set_thumbnail(url="https://b.ppy.sh/thumb/{}l.jpg".format(s_id))
                        await client.edit_message(message, "Spectating {}...".format(user), embed=emb)

        api_in_last_logged += 5 * len(spectating_users)

        spectating_users = new_list
    except Exception as e:
        await client.send_message(logging_channel, "<@203322898079809537> Something's gone wrong\n{}".format(e))

async def spectate_recent_loop():
    while True:
        await asyncio.sleep(int(60 / (30 / (max(len(spectating_users), 1) * 5))) + 10)
        await spectate_recent()

async def log():
    global logging, logging_message, logging_channel, api_in_last_logged, api_peak, last_api_log_time
    try:
        if api_peak < api_in_last_logged:
            api_peak = api_in_last_logged
        if logging:
            log_message_text = "Logging...\n{} continuous API requests in the last 120 seconds.\n(Peak is {})".format(api_in_last_logged, api_peak)
            if time.time() > last_api_log_time+120:
                last_api_log_time = time.time()
                if api_in_last_logged > 120:
                    await client.send_message(logging_channel, "<@203322898079809537> There have been over 100 continuous API requests in the last 120 seconds. Shutting down.")
                    sys.exit(1)
                api_in_last_logged = 0
            now = int(time.time())
            d = divmod(now - on_time, 86400)  # days
            h = divmod(d[1], 3600)  # hours
            m = divmod(h[1], 60)  # minutes
            s = m[1]  # seconds
            time_ago = ""
            if d[0] > 0:
                if int(d[0]) == 1:
                    time_ago += "1 day, "
                else:
                    time_ago += "{} days, ".format(int(d[0]))
            if h[0] > 0:
                if int(h[0]) == 1:
                    time_ago += "1 hour, "
                else:
                    time_ago += "{} hours, ".format(int(h[0]))
            if m[0] > 0:
                if int(m[0]) == 1:
                    time_ago += "1 minute, "
                else:
                    time_ago += "{} minutes, ".format(int(m[0]))
            if int(s) == 1:
                time_ago += "1 second"
            else:
                time_ago += "{} seconds".format(int(s))
            log_message_text += "\nUptime: {}\nTurned on at {} (UTC time)\nLast updated at {} (UTC time)".format(time_ago,
                                                                                                                datetime.utcfromtimestamp(on_time).strftime('%Y-%m-%d %H:%M:%S'),
                                                                                                                datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

            await client.edit_message(logging_message, log_message_text)
    except Exception as e:
        await client.send_message(logging_channel, "<@203322898079809537> Something's gone wrong\n{}".format(e))

async def log_loop():
    while True:
        await asyncio.sleep(5)
        await log()

async def low_detail_spectate_recent():
    global low_detail_spectating_users, api_in_last_logged, logging_channel, rolling, roll_number, rolling_channel

    try:
        new_list = []

        for message, user, time_ in low_detail_spectating_users:
            if (time.time() > time_ + 3600):
                await client.edit_message(message, "Timeout (1 hour): Stopped spectating {}.".format(user))
            else:
                new_list.append((message, user, time_))
                play_list, title_s, link_s, diff_s, user_info_s, user_link, user_pfp, b_id, s_id = recent.return_recent(
                    user, 0, 1, 0, True)
                if play_list != 5:
                    if len(play_list[0]) <= 1:
                        await client.edit_message(message, "Spectating {}... (Low detail)\n{} has no recent plays!".format(user, user))
                    else:
                        emb = discord.Embed(title=title_s, description=diff_s, url=link_s)
                        emb.set_author(name=user_info_s, url=user_link, icon_url=user_pfp)
                        emb.set_thumbnail(url="https://b.ppy.sh/thumb/{}l.jpg".format(s_id))
                        await client.edit_message(message, "Spectating {}... (Low detail)".format(user), embed=emb)

        api_in_last_logged += 2 * len(low_detail_spectating_users)

        low_detail_spectating_users = new_list
    except Exception as e:
        await client.send_message(logging_channel, "<@203322898079809537> Something's gone wrong\n{}".format(e))

async def low_detail_spectate_recent_loop():
    while True:
        await asyncio.sleep(int(60 / (30 / (max(len(low_detail_spectating_users), 1) * 2))) + 10)
        await low_detail_spectate_recent()

async def auto_roll():
    global rolling, roll_number, rolling_channel, rolling_message
    if rolling:
        await client.send_message(message.channel,
                                  "Autorolling: {} out of {}.".format(user_id, random.randint(1, roll_number),
                                                                      roll_number))

async def auto_roll_loop():
    while True:
        await asyncio.sleep(1)
        for i in range(5):
            await auto_roll()

def stop():
    task.cancel()

@client.event
async def on_message(message):
    global last_beatmap, spectating_users, logging_channel, logging_message, logging, low_detail_spectating_users, rolling, roll_number, rolling_channel
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    try:
        if message.content.startswith('~shutdown'):
            user_id = message.author.id
            if str(user_id) != "203322898079809537":
                await client.send_message(message.channel, "Only MBmasher can close the bot.")
            else:
                await client.send_message(message.channel, "Shutting down.")
                sys.exit(1)

        if message.content.startswith('~recent') or message.content.startswith('~rs') or message.content.startswith(
                '~r') and not message.content.startswith('~rb') and not message.content.startswith('~roll'):

            number_bool = False
            number = 1
            user_id = message.author.id

            fin = open('links.txt', 'r+')
            lines = [line.rstrip() for line in fin.readlines()]
            found = False
            for line in lines:
                space_split = line.split(" ")
                if space_split[0] == str(user_id):
                    author = " ".join(space_split[1:])
                    found = True
                    break

            if not found and len(message.content.split(" ")) <= 2 and not message.content.split(" ")[-1].isdigit():
                author = [0]
                await client.send_message(message.channel, "Link your account using ~link username")

            if len(message.content.split(" ")) > 1:
                if message.content.split(" ")[1].isdigit():
                    number = int(message.content.split(" ")[1])
                    number_bool = True
                if (len(message.content.split(" ")) > 2 and number_bool) or not number_bool:
                    author = " ".join(message.content.split(" ")[1 + number_bool:])
            if number > 49:
                await client.send_message(message.channel, "Please use a number smaller than 50!")
            else:
                play_list, title_s, link_s, diff_s, user_info_s, user_link, user_pfp, b_id, s_id = recent.return_recent(
                    author, 0, number, 0, False)
                if play_list != 5:
                    if len(play_list[0]) <= 1:
                        await client.send_message(message.channel, "{} has no recent plays!".format(author))
                    else:
                        last_beatmap = b_id
                        emb = discord.Embed(title=title_s, description=diff_s, url=link_s)
                        emb.set_author(name=user_info_s, url=user_link, icon_url=user_pfp)
                        emb.set_thumbnail(url="https://b.ppy.sh/thumb/{}l.jpg".format(s_id))
                        await client.send_message(message.channel, embed=emb)

        if message.content.startswith('~best') or message.content.startswith('~top'):
            number_bool = False
            number = 1
            user_id = message.author.id

            fin = open('links.txt', 'r+')
            lines = [line.rstrip() for line in fin.readlines()]
            found = False
            for line in lines:
                space_split = line.split(" ")
                if space_split[0] == str(user_id):
                    author = " ".join(space_split[1:])
                    found = True
                    break

            if not found and len(message.content.split(" ")) <= 2 and not message.content.split(" ")[-1].isdigit():
                author = [0]
                await client.send_message(message.channel, "Link your account using ~link username")

            if len(message.content.split(" ")) > 1:
                if message.content.split(" ")[1].isdigit():
                    number = int(message.content.split(" ")[1])
                    number_bool = True
                if (len(message.content.split(" ")) > 2 and number_bool) or not number_bool:
                    author = " ".join(message.content.split(" ")[1 + number_bool:])

            if number > 99:
                await client.send_message(message.channel, "Please use a number smaller than 100!")
            else:
                play_list, title_s, link_s, diff_s, user_info_s, user_link, user_pfp, b_id, s_id = recent.return_recent(
                    author, 1, number, 0, False)
                if play_list != 5:
                    if len(play_list[0]) <= 1:
                        await client.send_message(message.channel, "{} has no top plays! (wtf)".format(author))
                    else:
                        last_beatmap = b_id
                        emb = discord.Embed(title=title_s, description=diff_s, url=link_s)
                        emb.set_author(name=user_info_s, url=user_link, icon_url=user_pfp)
                        emb.set_thumbnail(url="https://b.ppy.sh/thumb/{}l.jpg".format(s_id))
                        await client.send_message(message.channel, embed=emb)

        if message.content.startswith('~compare') or message.content.startswith('~c'):
            number_bool = False
            number = 1
            user_id = message.author.id

            fin = open('links.txt', 'r+')
            lines = [line.rstrip() for line in fin.readlines()]
            found = False
            for line in lines:
                space_split = line.split(" ")
                if space_split[0].lower() == str(user_id).lower():
                    author = " ".join(space_split[1:])
                    found = True
                    break

            if not found and len(message.content.split(" ")) <= 2 and not message.content.split(" ")[-1].isdigit():
                author = [0]
                await client.send_message(message.channel, "Link your account using ~link username")

            if len(message.content.split(" ")) > 1:
                if message.content.split(" ")[1].isdigit():
                    number = int(message.content.split(" ")[1])
                    number_bool = True
                if (len(message.content.split(" ")) > 2 and number_bool) or not number_bool:
                    author = " ".join(message.content.split(" ")[1 + number_bool:])

            if number > 99:
                await client.send_message(message.channel, "Please use a number smaller than 100!")
            else:
                play_list, title_s, link_s, diff_s, user_info_s, user_link, user_pfp, b_id, s_id = recent.return_recent(
                    author, 2,
                    number,
                    last_beatmap, False)
                if play_list != 5:
                    if len(play_list[0]) <= 1:
                        await client.send_message(message.channel,
                                                  "{} has no plays on this beatmap!".format(author))
                    elif link_s == 0:
                        play = "play"
                        if len(play_list) > 1:
                            play += "s"
                        await client.send_message(message.channel,
                                                  "{} has no more than {} {} on this beatmap!".format(author, len(
                                                      play_list), play))
                    else:
                        emb = discord.Embed(title=title_s, description=diff_s, url=link_s)
                        emb.set_author(name=user_info_s, url=user_link, icon_url=user_pfp)
                        emb.set_thumbnail(url="https://b.ppy.sh/thumb/{}l.jpg".format(s_id))
                        await client.send_message(message.channel, embed=emb)

        if message.content.startswith('~recentbest') or message.content.startswith('~rb'):
            number_bool = False
            number = 1
            user_id = message.author.id

            fin = open('links.txt', 'r+')
            lines = [line.rstrip() for line in fin.readlines()]
            found = False
            for line in lines:
                space_split = line.split(" ")
                if space_split[0].lower() == str(user_id).lower():
                    author = " ".join(space_split[1:])
                    found = True
                    break

            if not found and len(message.content.split(" ")) <= 2 and not message.content.split(" ")[-1].isdigit():
                author = [0]
                await client.send_message(message.channel, "Link your account using ~link username")

            if len(message.content.split(" ")) > 1:
                if message.content.split(" ")[1].isdigit():
                    number = int(message.content.split(" ")[1])
                    number_bool = True
                if (len(message.content.split(" ")) > 2 and number_bool) or not number_bool:
                    author = " ".join(message.content.split(" ")[1 + number_bool:])
            if number > 99:
                await client.send_message(message.channel, "Please use a number smaller than 100!")
            else:
                play_list, title_s, link_s, diff_s, user_info_s, user_link, user_pfp, b_id, s_id = recent.return_recent(
                    author, 3,
                    number, 0, False)
                if play_list != 5:
                    if len(play_list) < 1:
                        await client.send_message(message.channel, "{} has no top plays! (wtf)".format(author))
                    else:
                        last_beatmap = b_id
                        emb = discord.Embed(title=title_s, description=diff_s, url=link_s)
                        emb.set_author(name=user_info_s, url=user_link, icon_url=user_pfp)
                        emb.set_thumbnail(url="https://b.ppy.sh/thumb/{}l.jpg".format(s_id))
                        await client.send_message(message.channel, embed=emb)

        if message.content.startswith('~roll'):
            number_bool = True
            number = 100
            user_id = message.author.id
            if len(message.content.split(" ")) > 1:
                if message.content.split(" ")[1].isdigit():
                    number = int(message.content.split(" ")[1])
                else:
                    number_bool = False
                    await client.send_message(message.channel, "Are you fucking stupid? That's not a number.")

            if number_bool:
                await client.send_message(message.channel,
                                          "<@{}> rolled a {} out of {}.".format(user_id, random.randint(1, number),
                                                                            number))

        if message.content.startswith('~autoroll'):
            logging = True
            roll_number = 100
            if len(message.content.split(" ")) > 1:
                if message.content.split(" ")[1].isdigit():
                    roll_number = int(message.content.split(" ")[1])
            if rolling_channel is not None:
                await client.send_message(message.channel, "Autorolling moved to this channel.")
                rolling_channel = message.channel
            else:
                await client.send_message(message.channel, "Started autorolling.")
                rolling_channel = message.channel

        if message.content.startswith('~unautoroll'):
            rolling = False

            if rolling_channel is not None:
                await client.send_message(message.channel, "Stopped autorolling.")
            else:
                await client.send_message(message.channel, "Not autorolling.")

        if message.content.startswith('~link'):
            name = ""
            if len(message.content.split(" ")) > 1:
                name = " ".join(message.content.split(" ")[1:])

            user_id = message.author.id
            fin = open('links.txt', 'r+')
            lines_to_write = []
            lines = [line.rstrip() for line in fin.readlines()]
            for line in lines:
                space_split = line.split(" ")
                if space_split[0] != str(user_id):
                    lines_to_write.append(line + '\n')

            fin.truncate(0)

            fin.seek(0)

            if len(lines_to_write) > 0:
                for line in lines_to_write:
                    fin.write(line)

            if name == "":
                await client.send_message(message.channel, "Type your username so you can be linked.")
            else:
                fin.write("{} {}\n".format(str(user_id), name))
                await client.send_message(message.channel,
                                          "<@{}> successfully linked to {}!".format(str(user_id), name))
            fin.close()

        if message.content.startswith('~spectate') or message.content.startswith('~spec'):
            low_detail = False
            listing = False
            if len(message.content.split(" ")) > 2 and message.content.split(" ")[-1] == "+low-detail":
                low_detail = True
            if len(message.content.split(" ")) > 1 and message.content.split(" ")[-1] == "+list":
                listing = True
                await client.send_message(message.channel,
                                          "Current list of spectated users: {}\n{}".format(
                                              ", ".join([i[1] for i in spectating_users]), ", ".join([i[1] for i in low_detail_spectating_users])))
            if not listing:
                if len(spectating_users) + len(low_detail_spectating_users) >= 5:
                    await client.send_message(message.channel,
                                              "Cannot spectate more than 5 users at a time.\nCurrent list of spectated users: {}\n{}\nUnspectate one of these users if you'd like to spectate a different user.".format(
                                              ", ".join([i[1] for i in spectating_users]), ", ".join([i[1] for i in low_detail_spectating_users])))
                else:
                    if len(message.content.split(" ")) > 1:
                        if low_detail:
                            spectate_user = " ".join(message.content.split(" ")[1:-1])
                        else:
                            spectate_user = " ".join(message.content.split(" ")[1:])
                        low_detail_text = ""
                        if low_detail:
                            low_detail_text = " (Low detail)"
                        client.send_message(message.channel, "test")
                        spectate_message = await client.send_message(message.channel, "Spectating {}...{}".format(spectate_user, low_detail_text))

                        if not low_detail:
                            spectating_users.append((spectate_message, spectate_user, time.time()))
                        else:
                            low_detail_spectating_users.append((spectate_message, spectate_user, time.time()))
                    else:
                        await client.send_message(message.channel, "Please specify a user to be spectated.")

        if message.content.startswith('~unspectate') or message.content.startswith('~unspec'):
            new_list = []
            low_detail_new_list = []
            if len(message.content.split(" ")) > 1:
                spectate_user = " ".join(message.content.split(" ")[1:])
                spectated_user = ""
                user_spectated = False
                for spectate_message, user, time_ in spectating_users:
                    if user.lower() == spectate_user.lower():
                        spectated_user = user
                        await client.edit_message(spectate_message, "Stopped spectating {}.".format(user))
                        user_spectated = True
                    else:
                        new_list.append((spectate_message, user, time_))

                for spectate_message, user, time_ in low_detail_spectating_users:
                    if user.lower() == spectate_user.lower():
                        spectated_user = user
                        await client.edit_message(spectate_message, "Stopped spectating {}.".format(user))
                        user_spectated = True
                    else:
                        low_detail_new_list.append((spectate_message, user, time_))

                if user_spectated:
                    spectating_users = new_list
                    low_detail_spectating_users = low_detail_new_list
                    await client.send_message(message.channel, "Stopped spectating {}".format(spectated_user))
                else:
                    await client.send_message(message.channel, "This user is not already being spectated.")
            else:
                await client.send_message(message.channel, "Please specify a user to be unspectated.")

        if message.content.startswith('~log'):
            logging = True
            if logging_message is not None:
                await client.edit_message(logging_message, "Logging stopped/moved.")
                logging_message = await client.send_message(message.channel, "Logging moved to this channel.")
                logging_channel = message.channel
            else:
                logging_message = await client.send_message(message.channel, "Started logging.")
                logging_channel = message.channel

    except Exception as e:
        await client.send_message(message.channel, "<@203322898079809537> Something's gone wrong\n{}".format(e))

@client.event
async def on_ready():
    global server

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

async def main():
    tasks = [
        client.start(TOKEN),
        spectate_recent_loop(),
        low_detail_spectate_recent_loop(),
        log_loop(),
        auto_roll_loop()
    ]

    while len(tasks):
        done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            print(task, task.result())


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()