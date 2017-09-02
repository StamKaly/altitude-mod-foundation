from threading import Thread
from janus import Queue
from random import randint
from . import bot, bot_database


class BotHandler:
    def __init__(self, bots):
        """
        :param bots: [*[login, youtube_key, server_id, voice_channel_id, text_channel_id]]
        """
        self.database = bot_database.BotDatabase()
        self.new_requests = []
        self.bots = []
        for bot_, number in zip(bots, range(1, len(bots) + 1)):
            loop = bot.asyncio.new_event_loop()
            commands_queue = Queue(loop=loop)
            output_queue = Queue(loop=loop)
            Thread(target=bot.bot,
                   args=(loop, bot_[0], number, commands_queue.async_q, output_queue.async_q, bot_[1],
                         bot_[2], bot_[3], bot_[4])
                   ).start()
            self.bots.append([commands_queue.sync_q, output_queue.sync_q, None,
                              output_queue.sync_q.get(), number])

    def get_output_queues(self):
        for bot_ in self.bots:
            yield bot_[1]

    def get_vapor_ids_for_bot(self, number, vapor_ids):
        for bot_ in self.bots:
            if bot_[4] == number:
                return self.database.get_in_channel(vapor_ids, [member.id for member in bot_[3]])

    def get_bot(self, vapor_id):
        for bot_ in self.bots:
            discord_id = self.database.check_if_in_channel(vapor_id, [member.id for member in bot_[3]])
            if discord_id:
                return bot_, discord_id
        return None, None

    def check_who_left(self, vapor_id):
        for bot_ in self.bots:
            if bot_[2] and bot_[2].vapor_id == vapor_id:
                self.leave(bot_[2], None)

    def request(self, vapor_id):
        if not self.new_requests:
            number = randint(1000, 9999)
        else:
            found = False
            for request in self.new_requests:
                if request[1] == vapor_id:
                    number = request[0]
                    found = True
                    break
            if not found:
                numbers = [request[0] for request in self.new_requests]
                number = numbers[0]
                while number in numbers:
                    number = randint(1000, 9999)
        self.new_requests.append([number, vapor_id])
        self.bots[0][0].put(["request", [number, vapor_id]])
        return "Bots don't recognise you yet, please send your secret\n" \
               "number {} in channel #music_bots in discord.".format(number)

    def add_user(self, vapor_id, discord_id):
        self.database.add(vapor_id, discord_id)
        for request in self.new_requests:
            if request[1] == vapor_id:
                self.new_requests.remove(request)
                break

    def join(self, player):
        if not self.database.check_if_registered(player.vapor_id):
            return self.request(player.vapor_id)
        bot_list, discord_id = self.get_bot(player.vapor_id)
        if not bot_list:
            return "You aren't in any bot's voice channel."
        if bot_list[2]:
            return "{} has already requested bot {} to join its channel!".format(bot_list[2].nickname, bot_list[4])
        else:
            bot_list[0].put(["join", discord_id, player.vapor_id])
            bot_list[2] = player
            return "Bot {} is requested to join its channel!".format(bot_list[4])

    def leave(self, player, admin, safe_leave=False, number=None):
        if not self.database.check_if_registered(player.vapor_id):
            return self.request(player.vapor_id)
        if not safe_leave:
            bot_list, _ = self.get_bot(player.vapor_id)
        else:
            for bot_ in self.bots:
                if bot_[4] == number:
                    bot_list = bot_
                    break
        if not bot_list:
            return "You aren't in any bot's voice channel."
        if not bot_list[2]:
            return "Bot {} hasn't joined its voice channel yet.\nRun /join to request it to join!".format(bot_list[4])
        elif bot_list[2] == player or admin:
            bot_list[0].put(["leave"])
            bot_list[2] = None
            return "Bot {} is requested to leave its channel.".format(bot_list[4])
        else:
            return "You do not have permission to request bot {}\nto leave its channel right now.".format(bot_list[4])

    def play(self, player, search_terms):
        if not self.database.check_if_registered(player.vapor_id):
            return self.request(player.vapor_id)
        bot_list, _ = self.get_bot(player.vapor_id)
        if not bot_list:
            return "You aren't in any bot's voice channel."
        if not bot_list[2]:
            return "Bot {} hasn't joined its voice channel yet.\nRun /join to request it to join!".format(bot_list[4])
        else:
            bot_list[0].put(["play", search_terms, player])

    def pause(self, player, admin):
        if not self.database.check_if_registered(player.vapor_id):
            return self.request(player.vapor_id)
        bot_list, _ = self.get_bot(player.vapor_id)
        if not bot_list:
            return "You aren't in any bot's voice channel."
        if not bot_list[2]:
            return "Bot {} hasn't joined its voice channel yet.\nRun /join to request it to join!".format(bot_list[4])
        if bot_list[2] == player or admin:
            bot_list[0].put(["pause", player])
        else:
            return "You do not have permission to request bot {}\nto pause its stream right now.".format(bot_list[4])

    def resume(self, player, admin):
        if not self.database.check_if_registered(player.vapor_id):
            return self.request(player.vapor_id)
        bot_list, _ = self.get_bot(player.vapor_id)
        if not bot_list:
            return "You aren't in any bot's voice channel."
        if not bot_list[2]:
            return "Bot {} hasn't joined its voice channel yet.\nRun /join to request it to join!".format(bot_list[4])
        if bot_list[2] == player or admin:
            bot_list[0].put(["resume", player])
        else:
            return "You do not have permission to request bot {}\nto resume its stream right now.".format(bot_list[4])

    def volume(self, player, admin, volume):
        if not self.database.check_if_registered(player.vapor_id):
            return self.request(player.vapor_id)
        bot_list, _ = self.get_bot(player.vapor_id)
        if not bot_list:
            return "You aren't in any bot's voice channel."
        if not bot_list[2]:
            return "Bot {} hasn't joined its voice channel yet.\nRun /join to request it to join!".format(bot_list[4])
        elif bot_list[2] == player or admin:
            if not 1 <= int(volume) <= 200:
                return "Volume can be from 1 to 200%"
            bot_list[0].put(["volume", int(volume)/100, player])
        else:
            return "You do not have permission to request bot {}\nto change its volume right now.".format(bot_list[4])

    def skip(self, player, admin):
        if not self.database.check_if_registered(player.vapor_id):
            return self.request(player.vapor_id)
        bot_list, _ = self.get_bot(player.vapor_id)
        if not bot_list:
            return "You aren't in any bot's voice channel."
        if not bot_list[2]:
            return "Bot {} hasn't joined its voice channel yet.\nRun /join to request it to join!".format(bot_list[4])
        elif bot_list[2] == player or admin:
            bot_list[0].put(["skip", player])
        else:
            return "You do not have permission to request bot {}\nto skip current playing song right now."\
                .format(bot_list[4])
