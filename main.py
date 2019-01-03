import discord
import recent
import random
import os
import time
import asyncio
import sys

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


key = os.environ.get('API_KEY')
TOKEN = os.environ.get('TOKEN')

spectating_users = []

fin = open('keys.cfg', 'r+')
fin.truncate(0)
fin.seek(0)
fin.write("[osu]\napi_key = {}".format(key))
fin.close()

client = discord.Client()

last_beatmap = 0

async def spectate_recent():
    global spectating_users

    print(spectating_users)

    new_list = []

    for message, user, time_ in spectating_users:
        if (time.time() > time_ + 3600):
            await client.edit_message(message, "Timeout (1 hour): Stopped spectating {}.".format(user))
        else:
            new_list.append((message, user, time_))
            play_list, title_s, link_s, diff_s, user_info_s, user_link, user_pfp, b_id = recent.return_recent(
                user, 0, 1, 0)
            print(diff_s)
            if play_list != 5:
                if len(play_list[0]) <= 1:
                    await client.edit_message(message, "Spectating {}...\n{} has no recent plays!".format(user, user))
                else:
                    emb = discord.Embed(title=title_s, description=diff_s, url=link_s)
                    emb.set_author(name=user_info_s, url=user_link, icon_url=user_pfp)
                    await client.edit_message(message, "Spectating {}...".format(user), embed=emb)

    spectating_users = new_list
    await asyncio.sleep(30)
    await spectate_recent()

def stop():
    task.cancel()

@client.event
async def on_message(message):
    global last_beatmap, spectating_users
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('~shutdown'):
        user_id = message.author.id
        if str(user_id) != "203322898079809537":
            await client.send_message(message.channel, "Only MBmasher can close the bot.")
        else:
            await client.send_message(message.channel, "Shutting down.")
            sys.exit(1)

    if message.content.startswith('~recent') or message.content.startswith('~rs') or message.content.startswith(
            '~r') and not message.content.startswith('~rb') and not message.content.startswith('~roll'):

        try:
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

            if not found:
                author = [0]
                await client.send_message(message.channel, "Link your account using ~link username")

            if len(message.content.split(" ")) > 1:
                if message.content.split(" ")[1].isdigit():
                    number = int(message.content.split(" ")[1])
                    number_bool = True
                if (len(message.content.split(" ")) > 2 and number_bool) or not number_bool:
                    author = "_".join(message.content.split(" ")[1 + number_bool:])
            if number > 49:
                await client.send_message(message.channel, "Please use a number smaller than 50!")
            else:
                play_list, title_s, link_s, diff_s, user_info_s, user_link, user_pfp, b_id = recent.return_recent(
                    author, 0, number, 0)
                if play_list != 5:
                    if len(play_list[0]) <= 1:
                        await client.send_message(message.channel, "{} has no recent plays!".format(author))
                    else:
                        last_beatmap = b_id
                        emb = discord.Embed(title=title_s, description=diff_s, url=link_s)
                        emb.set_author(name=user_info_s, url=user_link, icon_url=user_pfp)
                        await client.send_message(message.channel, embed=emb)
        except:
            await client.send_message(message.channel, "<@203322898079809537> you fucked up dumbass")

    if message.content.startswith('~best') or message.content.startswith('~top'):
        try:
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

            if not found:
                author = [0]
                await client.send_message(message.channel, "Link your account using ~link username")

            if len(message.content.split(" ")) > 1:
                if message.content.split(" ")[1].isdigit():
                    number = int(message.content.split(" ")[1])
                    number_bool = True
                if (len(message.content.split(" ")) > 2 and number_bool) or not number_bool:
                    author = "_".join(message.content.split(" ")[1 + number_bool:])

            if number > 99:
                await client.send_message(message.channel, "Please use a number smaller than 100!")
            else:
                play_list, title_s, link_s, diff_s, user_info_s, user_link, user_pfp, b_id = recent.return_recent(
                    author, 1, number, 0)
                if play_list != 5:
                    if len(play_list[0]) <= 1:
                        await client.send_message(message.channel, "{} has no top plays! (wtf)".format(author))
                    else:
                        last_beatmap = b_id
                        emb = discord.Embed(title=title_s, description=diff_s, url=link_s)
                        emb.set_author(name=user_info_s, url=user_link, icon_url=user_pfp)
                        await client.send_message(message.channel, embed=emb)
        except:
            await client.send_message(message.channel, "<@203322898079809537> you fucked up dumbass")

    if message.content.startswith('~compare') or message.content.startswith('~c'):
        try:
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

            if not found:
                author = [0]
                await client.send_message(message.channel, "Link your account using ~link username")

            if len(message.content.split(" ")) > 1:
                if message.content.split(" ")[1].isdigit():
                    number = int(message.content.split(" ")[1])
                    number_bool = True
                if (len(message.content.split(" ")) > 2 and number_bool) or not number_bool:
                    author = "_".join(message.content.split(" ")[1 + number_bool:])

            if number > 99:
                await client.send_message(message.channel, "Please use a number smaller than 100!")
            else:
                play_list, title_s, link_s, diff_s, user_info_s, user_link, user_pfp, b_id = recent.return_recent(
                    author, 2,
                    number,
                    last_beatmap)
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
                        await client.send_message(message.channel, embed=emb)
        except:
            await client.send_message(message.channel, "<@203322898079809537> you fucked up dumbass")

    if message.content.startswith('~recentbest') or message.content.startswith('~rb'):
        try:
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

            if not found:
                author = [0]
                await client.send_message(message.channel, "Link your account using ~link username")

            if len(message.content.split(" ")) > 1:
                if message.content.split(" ")[1].isdigit():
                    number = int(message.content.split(" ")[1])
                    number_bool = True
                if (len(message.content.split(" ")) > 2 and number_bool) or not number_bool:
                    author = "_".join(message.content.split(" ")[1 + number_bool:])
            if number > 99:
                await client.send_message(message.channel, "Please use a number smaller than 100!")
            else:
                play_list, title_s, link_s, diff_s, user_info_s, user_link, user_pfp, b_id = recent.return_recent(
                    author, 3,
                    number, 0)
                if play_list != 5:
                    if len(play_list) < 1:
                        await client.send_message(message.channel, "{} has no top plays! (wtf)".format(author))
                    else:
                        last_beatmap = b_id
                        emb = discord.Embed(title=title_s, description=diff_s, url=link_s)
                        emb.set_author(name=user_info_s, url=user_link, icon_url=user_pfp)
                        await client.send_message(message.channel, embed=emb)
        except:
            await client.send_message(message.channel, "<@203322898079809537> you fucked up dumbass")

    if message.content.startswith('~roll'):
        try:
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
        except:
            await client.send_message(message.channel, "<@203322898079809537> you fucked up dumbass")

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
        print(spectating_users)
        if len(spectating_users) >= 3:
            await client.send_message(message.channel, "Cannot spectate more than 3 users at a time.\nCurrent list of spectated users: {}\nUnspectate one of these users if you'd like to spectate a different user.".format(", ".join(spectating_users)))
        else:
            if len(message.content.split(" ")) > 1:
                spectate_user = "_".join(message.content.split(" ")[1:])
                client.send_message(message.channel, "test")
                spectate_message = await client.send_message(message.channel, "Spectating {}...".format(spectate_user))
                spectating_users.append((spectate_message, spectate_user, time.time()))
            else:
                await client.send_message(message.channel, "Please specify a user to be spectated.")

    if message.content.startswith('~unspectate') or message.content.startswith('~unspec'):
        print(spectating_users)
        new_list = []
        if len(message.content.split(" ")) > 1:
            spectate_user = "_".join(message.content.split(" ")[1:])
            spectated_user = ""
            user_spectated = False
            for spectate_message, user, time_ in spectating_users:
                if user == spectate_user:
                    spectated_user = user
                    await client.edit_message(spectate_message, "Stopped spectating {}.".format(user))
                    user_spectated = True
                else:
                    new_list.append((spectate_message, user, time_))

            if user_spectated:
                spectating_users = new_list
                await client.send_message(message.channel, "Stopped spectating {}".format(spectated_user))
            else:
                await client.send_message(message.channel, "This user is not already being spectated.")
        else:
            await client.send_message(message.channel, "Please specify a user to be unspectated.")

    if (message.content.startswith('!r') or message.content.startswith('!rb') or message.content.startswith(
            '!recent')
            or message.content.startswith('!top') or message.content.startswith(
                '!best') or message.content.startswith('!rs') or
            message.content.startswith('>r') or message.content.startswith('>rb') or message.content.startswith(
                '>recent') or message.content.startswith('>top') or message.content.startswith(
                '>best') or message.content.startswith('>rs') or message.content.startswith('>roll')
            or message.content.startswith('!roll')):
        user_id = message.author.id
        if str(user_id) == "138585010784436224":
            await client.send_message(message.channel,
                                      "fuck you <@138585010784436224>")
            await client.send_message(message.channel,
                                      "fuck you <@138585010784436224>")
            await client.send_message(message.channel,
                                      "fuck you <@138585010784436224>")
            await client.send_message(message.channel,
                                      "fuck you <@138585010784436224>")
            await client.send_message(message.channel,
                                      "fuck you <@138585010784436224>")
        else:
            await client.send_message(message.channel,
                                  "I'm online, use me!! (I'm definitely cooler than BoatBot or owo)")

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
        spectate_recent()
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