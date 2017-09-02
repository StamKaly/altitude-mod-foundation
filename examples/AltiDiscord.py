from .altitude import AltitudeMod
from .alti_discord import BotHandler


class AltiDiscord(AltitudeMod):
    def initialize(self, bots):
        self.bot_handler = BotHandler(bots)

    def _run_on_every_loop(self):
        for output_queue in self.bot_handler.get_output_queues():
            while not output_queue.empty():
                output = output_queue.get()
                if output[0] == 'user':
                    self.bot_handler.add_user(output[1][0], output[1][1])
                elif output[0] == 'whisper':
                    self.commands.whisper(output[1].nickname, output[2])
                elif output[0] == 'safeLeave':
                    self.bot_handler.leave(self.players.player_from_vapor_id(output[1]), False,
                                           safe_leave=True, number=output[2])
                else:
                    for vapor_id in self.bot_handler.get_vapor_ids_for_bot(output[0], self.players.get_all_vapor_ids()):
                        self.commands.whisper(self.players.player_from_vapor_id(vapor_id).nickname, output[1])

    def on_client_remove(self, nickname, vapor_id, ip, reason):
        self.bot_handler.check_who_left(vapor_id)

    def on_command(self, player, command_name, arguments, group):
        if command_name == "join":
            self.commands.whisper(player.nickname, self.bot_handler.join(player))
        elif command_name == "leave":
            self.commands.whisper(player.nickname, self.bot_handler.leave(player,
                                                                          True if group == "Administrator" else False))
        elif command_name == "play":
            output = self.bot_handler.play(player, arguments[0])
            if output:
                self.commands.whisper(player.nickname, output)
        elif command_name == "pause":
            output = self.bot_handler.pause(player, True if group == "Administrator" else False)
            if output:
                self.commands.whisper(player.nickname, output)
        elif command_name == "resume":
            output = self.bot_handler.resume(player, True if group == "Administrator" else False)
            if output:
                self.commands.whisper(player.nickname, output)
        elif command_name == "volume":
            output = self.bot_handler.volume(player, True if group == "Administrator" else False, arguments[0])
            if output:
                self.commands.whisper(player.nickname, output)
        elif command_name == "skip":
            output = self.bot_handler.skip(player, True if group == "Administrator" else False)
            if output:
                self.commands.whisper(player.nickname, output)


if __name__ == '__main__':
    mod = AltiDiscord(27275, '/home/user/altitude')
    youtube_key = 'my youtube key'
    discord_server_id = 'discord server id'
    discord_text_channel_id = 'discord text channel id'
    mod.initialize([
        [['email', 'password'], youtube_key, discord_server_id, "bot's voice channel id", discord_text_channel_id],
        ["bot's token", youtube_key, discord_server_id, "bot's voice channel id", discord_text_channel_id]
    ])
    mod.run()
