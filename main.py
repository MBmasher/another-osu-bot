import discord
import recent
import random
import os

key = os.environ.get('API_KEY')
TOKEN = os.environ.get('TOKEN')

fin = open('keys.cfg', 'r+')
fin.truncate(0)
fin.seek(0)
fin.write("[osu]\napi_key = {}".format(key))
fin.close()

client = discord.Client()

last_beatmap = 0

@client.event
async def on_message(message):
    global last_beatmap
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

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
        except Exception as e:
            await client.send_message(message.channel, "<@203322898079809537> you fucked up dumbass\n{}".format(e))

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
        except Exception as e:
            await client.send_message(message.channel, "<@203322898079809537> you fucked up dumbass\n{}".format(e))

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
        except Exception as e:
            await client.send_message(message.channel, "<@203322898079809537> you fucked up dumbass\n{}".format(e))

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
        except Exception as e:
            await client.send_message(message.channel, "<@203322898079809537> you fucked up dumbass\n{}".format(e))

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
        except Exception as e:
            await client.send_message(message.channel, "<@203322898079809537> you fucked up dumbass\n{}".format(e))

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

    if (message.content.startswith('!r') or message.content.startswith('!rb') or message.content.startswith(
            '!recent')
            or message.content.startswith('!top') or message.content.startswith(
                '!best') or message.content.startswith('!rs') or
            message.content.startswith('>r') or message.content.startswith('>rb') or message.content.startswith(
                '>recent') or message.content.startswith('>top') or message.content.startswith(
                '>best') or message.content.startswith('>rs') or message.content.startswith('>roll')
            or message.content.startswith('!roll')):
        await client.send_message(message.channel,
                                  "I'm online, use me!! (I'm definitely cooler than BoatBot or owo)")

@client.event
async def on_ready():
    global server
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)