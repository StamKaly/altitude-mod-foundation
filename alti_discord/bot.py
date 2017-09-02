import discord
import asyncio
import aiohttp
import async_timeout
import json


class DiscordMusic(discord.Client):
    def __init__(self, number, commands_queue, output_queue, youtube_key, server_id, voice_channel_id, text_channel_id):
        discord.Client.__init__(self)
        self.number = number
        self.commands_queue = commands_queue
        self.output_queue = output_queue
        discord.opus.load_opus('/usr/lib/x86_64-linux-gnu/libopus.so.0')
        self.youtube_key = youtube_key
        self.server = server_id
        self.voice_channel = voice_channel_id
        self.text_channel = text_channel_id
        self.players = []
        self.current_player = None
        self.new_requests = []
        self.alti_player = None
        self.current_volume = 1.00

    async def bot_play_from_players(self):
        if self.players and self.is_voice_connected(self.server):
            if self.players and not self.current_player:
                self.current_player = self.players[0]
                self.players.remove(self.players[0])
                self.current_player.volume = self.current_volume
                self.current_player.start()
            if self.current_player.is_done():
                self.current_player = None

    async def on_ready(self):
        self.voice_channel = self.get_channel(self.voice_channel)
        await self.output_queue.put(self.voice_channel.voice_members)
        self.text_channel = self.get_channel(self.text_channel)
        self.server = self.get_server(self.server)
        await self.send_message(self.text_channel, "Started")
        while True:
            if not self.commands_queue.empty():
                command = await self.commands_queue.get()
                if command[0] == "join":
                    await self.bot_join_voice_channel(command[1], command[2])
                elif command[0] == "leave":
                    await self.bot_leave_voice_channel()
                elif command[0] == "play":
                    url = await self.youtube_search(command[1])
                    if url:
                        await self.bot_add_music_url(url, command[2].nickname)
                    else:
                        await self.output_queue.put(['whisper', command[2],
                                                     'No video was found with your search terms!'])
                elif command[0] == "pause":
                    await self.bot_pause(command[1])
                elif command[0] == "resume":
                    await self.bot_resume(command[1])
                elif command[0] == "volume":
                    await self.bot_change_volume(command[1], command[2])
                elif command[0] == "skip":
                    await self.bot_skip(command[1])
                elif command[0] == "request":
                    self.new_requests.append(command[1])
            await self.bot_play_from_players()
            await asyncio.sleep(0.1)

    async def on_message(self, message):
        if all((self.new_requests, message.channel == self.text_channel, len(message.content) == 4,
                message.author.id != self.user.id, message.content.isdigit())):
            found = False
            for request in self.new_requests:
                if message.content == str(request[0]):
                    await self.output_queue.put(['user', [request[1], message.author.id]])
                    self.new_requests.remove(request)
                    await self.send_message(message.channel,
                                            "{}, you successfully registered!".format(message.author.mention))
                    found = True
                    break
            if not found:
                await self.send_message(message.channel,
                                        "{}, sorry but your secret number was not found.".format(message.author.mention)
                                        )

    async def on_voice_state_update(self, before, after):
        if self.alti_player and self.alti_player[0] not in [member.id for member in self.voice_channel.voice_members]:
            await self.output_queue.put(['safe_leave', self.alti_player[1], self.number])

    async def bot_join_voice_channel(self, discord_id, vapor_id):
        if not self.is_voice_connected(self.server):
            self.alti_player = (discord_id, vapor_id)
            await self.join_voice_channel(self.voice_channel)
        else:
            print("Warning: Requested to join when already connected!")

    async def bot_leave_voice_channel(self):
        if self.is_voice_connected(self.server):
            self.players = []
            self.current_player = None
            self.alti_player = None
            self.current_volume = 1.00
            await self.voice_client_in(self.server).disconnect()
        else:
            print("Warning: Requested to leave when not connected!")

    async def youtube_search(self, search_terms):
        search_terms = ','.join(search_terms.split())
        url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&q={}&type=video&key={}'.format(search_terms,
                                                                                                        self.youtube_key
                                                                                                        )
        async with aiohttp.ClientSession(loop=self.loop) as session:
            with async_timeout.timeout(10):
                async with session.get(url) as response:
                    try:
                        json_response = await response.json()
                        if not json_response['pageInfo']['totalResults'] == 0:
                            return 'http://youtube.com/watch?v={}'.format(json_response['items'][0]['id']['videoId'])
                    except json.decoder.JSONDecodeError:
                        return None

    async def bot_add_music_url(self, url, nickname):
        if self.is_voice_connected(self.server):
            player = await self.voice_client_in(self.server).create_ytdl_player(url)
            self.players.append(player)
            try:
                if player.title:
                    string = "{} enqueued {}.".format(nickname, player.title)
                    string.encode('ascii')
                    await self.output_queue.put([self.number, string])
            except UnicodeEncodeError:
                pass

    async def bot_pause(self, alti_player):
        if self.current_player and self.current_player.is_playing():
            self.current_player.pause()
            await self.output_queue.put([self.number, "Bot {} has paused the stream.".format(self.number)])
        else:
            await self.output_queue.put(['whisper', alti_player, 'Nothing is being streamed in order to pause.'])

    async def bot_resume(self, alti_player):
        if self.current_player and not self.current_player.is_playing():
            self.current_player.resume()
            await self.output_queue.put([self.number, "Bot {} has resumed the stream.".format(self.number)])
        else:
            await self.output_queue.put(['whisper', alti_player, 'Nothing has been paused in order to resume.'])

    async def bot_change_volume(self, volume, alti_player):
        if self.current_player:
            current_volume = int(self.current_player.volume * 100)
            self.current_volume = volume
            self.current_player.volume = volume
            await self.output_queue.put([self.number,
                                         "Bot {} has changed the stream's volume\nfrom {}% to {}%.".format(
                                             self.number, current_volume, int(volume * 100))])
        else:
            await self.output_queue.put(['whisper', alti_player,
                                         'Nothing is being streamed in order to change volume.'])

    async def bot_skip(self, alti_player):
        if self.current_player and self.current_player.is_playing():
            self.current_player.stop()
            self.current_player = None
            await self.output_queue.put([self.number,
                                         "Bot {} has stopped streaming current playing song!".format(self.number)])
        else:
            await self.output_queue.put(['whisper', alti_player, 'No song is being played in order to skip it.'])


def bot(loop, login, number, commands_queue, output_queue, youtube_key, server_id, voice_channel_id, text_channel_id):
    asyncio.set_event_loop(loop)
    login = login if len(login) == 2 else [login]
    DiscordMusic(number, commands_queue, output_queue, youtube_key, server_id, voice_channel_id, text_channel_id)\
        .run(*login)
