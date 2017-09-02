class Commands:
    def __init__(self, players_object, port, command_file):
        self.players = players_object
        self.command_file = command_file
        self.console = "{},console,".format(port)

    def write_command(self, cmd):
        with open(self.command_file, "a") as commands:
            commands.write("{}\n".format(cmd))
    
    @staticmethod
    def aquote(nickname):
        return nickname.replace('\\', '\\\\').replace('"', '\\"')

    def start_tournament(self):
        """
        Starts server's Tournament Mode.
        """
        cmd = '{}startTournament'.format(self.console)
        self.write_command(cmd)

    def stop_tournament(self):
        """
        Turns server's Tournament Mode off.
        """
        cmd = '{}stopTournament'.format(self.console)
        self.write_command(cmd)

    def add_ban(self, vapor_id_or_ip, duration, unit_time, reason):
        """
        Makes target player receive a ban.
        :param vapor_id_or_ip: Player's Vapor ID or IP to be banned
        :param duration: A number between 1 and 9999
        :param unit_time: "minute", "day", "hour", "week" or "forever" for years
        :param reason: A reason for the ban
        """
        identity = vapor_id_or_ip if len(vapor_id_or_ip) == 36 else vapor_id_or_ip.split(":")[0] \
            if ':' in vapor_id_or_ip else vapor_id_or_ip
        cmd = '{}addBan {} {} {} "{}"'.format(self.console, identity, duration, unit_time, Commands.aquote(reason))
        self.write_command(cmd)

    def add_chat_block(self, vapor_id_or_ip, block_type, duration, unit_time, reason):
        """
        Makes target player receive a chat block.
        :param vapor_id_or_ip: Player's Vapor ID or IP
        :param block_type: "AllChat" or "TeamChat"
        :param duration: A number between 1 and 9999
        :param unit_time: "minute", "day", "hour", "week" or "forever" for years
        :param reason: A reason for the chat block
        """
        identity = vapor_id_or_ip if len(vapor_id_or_ip) == 36 else vapor_id_or_ip.split(":")[0] \
            if ':' in vapor_id_or_ip else vapor_id_or_ip
        cmd = '{}addChatBlock {} {} {} {} "{}"'.format(self.console, identity, block_type, duration,
                                                       unit_time, Commands.aquote(reason))
        self.write_command(cmd)

    def ban(self, nickname, duration, unit_time, reason):
        """
        Makes target player receive a ban.
        :param nickname: Player's nickname
        :param duration: A number between 1 and 9999
        :param unit_time: "minute", "day", "hour", "week" or "forever" for years
        :param reason: A reason for the ban
        """
        cmd = '{}ban "{}" {} {} "{}"'.format(self.console, Commands.aquote(nickname), duration,
                                             unit_time, Commands.aquote(reason))
        self.write_command(cmd)

    def chat_block(self, nickname, block_type, duration, unit_time, reason):
        """
        Makes target player receive a chat block.
        :param nickname: Player's nickname
        :param block_type: "AllChat" or "TeamChat"
        :param duration: A number between 1 and 9999
        :param unit_time: "minute", "day", "hour", "week" or "forever" for years
        :param reason: A reason for the chat block
        """
        cmd = '{}chatBlock "{}" {} {} {} "{}"'.format(self.console, Commands.aquote(nickname), block_type,
                                                      duration, unit_time, Commands.aquote(reason))
        self.write_command(cmd)

    def remove_ban(self, vapor_id_or_ip):
        """
        Removes target player's ban.
        :param vapor_id_or_ip: Player's Vapor ID or IP
        """
        identity = vapor_id_or_ip if len(vapor_id_or_ip) == 36 else vapor_id_or_ip.split(":")[0] \
            if ':' in vapor_id_or_ip else vapor_id_or_ip
        cmd = '{}removeBan {}'.format(self.console, identity)
        self.write_command(cmd)

    def remove_chat_block(self, vapor_id_or_ip, block_type):
        """
        Removes target player's chat block.
        :param vapor_id_or_ip: Player's Vapor ID or IP
        :param block_type: "AllChat" or "TeamChat"
        """
        identity = vapor_id_or_ip if len(vapor_id_or_ip) == 36 else vapor_id_or_ip.split(":")[0] \
            if ':' in vapor_id_or_ip else vapor_id_or_ip
        cmd = "{}removeChatBlock {} {}".format(self.console, identity, block_type)
        self.write_command(cmd)

    def change_server(self, nickname, ip, secret_code):
        """
        Moves target player to a different server.
        :param nickname: Player's nickname to be moved
        :param ip: IP address:port of the target server
        :param secret_code: Target server's password or None if there isn't one
        """
        secret_code = secret_code or "pw"
        cmd = '{}serverRequestPlayerChangeServer "{}" {} {}'.format(self.console, Commands.aquote(nickname),
                                                                    ip, Commands.aquote(secret_code))
        self.write_command(cmd)

    def all_change_server(self, ip, secret_code):
        """
        Moves all players in server to a different server.
        :param ip: IP address:port of the target server
        :param secret_code: Target server's password or None if there isn't one
        """
        secret_code = secret_code or "pw"
        for nickname in self.players.all_nicknames():
            cmd = '{}serverRequestPlayerChangeServer "{}" {} {}'.format(self.console, Commands.aquote(nickname),
                                                                        ip, Commands.aquote(secret_code))
            self.write_command(cmd)

    def whisper(self, nickname, message):
        """
        Uses the server to whisper a single message to target player.
        :param nickname: Player's nickname to be whispered
        :param message:
        """
        if '\n' not in message:
            cmd = '{}serverWhisper "{}" "{}"'.format(self.console, Commands.aquote(nickname), Commands.aquote(message))
            self.write_command(cmd)
        else:
            self.multiple_whispers(nickname, message.split('\n'))

    def multiple_whispers(self, nickname, messages):
        """
        Uses the server to whisper multiple messages to target player
        :param nickname: Player's nickname to be whispered
        :param messages: A list of messages to send
        """
        for message in messages:
            cmd = '{}serverWhisper "{}" "{}"'.format(self.console, Commands.aquote(nickname), Commands.aquote(message))
            self.write_command(cmd)

    def message(self, message):
        """
        Uses the server to send a single message viewable from all the players.
        :param message: A string of message to send
        """
        if '\n' not in message:
            cmd = '{}serverMessage "{}"'.format(self.console, Commands.aquote(message))
            self.write_command(cmd)
        else:
            self.multiple_messages(message.split('\n'))

    def multiple_messages(self, messages):
        """
        Uses the server to send multiple messages viewable from all the players.
        :param messages: A list of messages to send
        """
        for message in messages:
            cmd = '{}serverMessage "{}"'.format(self.console, Commands.aquote(message))
            self.write_command(cmd)

    def log_server_status(self):
        """
        Logs all players' information in case someone's was lost
        """
        cmd = '{}logServerStatus'.format(self.console)
        self.write_command(cmd)

    def log_plane_positions(self):
        """
        Logs each player's plane position on the map for parsing.
        """
        cmd = '{}logPlanePositions'.format(self.console)
        self.write_command(cmd)

    def change_map(self, map_name):
        """
        Changes the map of the server.
        :param map_name: The name of the map
        """
        cmd = '{}changeMap {}'.format(self.console, map_name)
        self.write_command(cmd)

    def camera_scale(self, camera):
        """
        Modifies the scale of each player's camera.
        :param camera: A number between 40 and 300
        """
        cmd = '{}testCameraViewScale {}'.format(self.console, camera)
        self.write_command(cmd)

    def plane_scale(self, scale):
        """
        Modifies the scale of each player's plane.
        :param scale: A number between 40 and 300
        """
        cmd = '{}testPlaneScale {}'.format(self.console, scale)
        self.write_command(cmd)

    def gravity_modifier(self, mode):
        """
        Modifies the gravity to different objects.
        :param mode: "nothing", "planes", "powerups", "everything"
        """
        if mode == "nothing":
            mode = 0
        elif mode == "planes":
            mode = 1
        elif mode == "powerups":
            mode = 2
        elif mode == "everything":
            mode = 3
        cmd = '{}testGravityMode {}'.format(self.console, mode)
        self.write_command(cmd)

    def health_modifier(self, health):
        """
        Modifies the health each player has. Takes effect only to those who
        spawn after the modification.
        :param health: A number between 1 and 999
        """
        cmd = '{}testHealthModifier {}'.format(self.console, health)
        self.write_command(cmd)

    def disable_weapon(self, weapon):
        """
        Changes what weapons are allowed for players to use.
        :param weapon: "nothing", "main", "secondary", "everything"
        """
        if weapon == "nothing":
            weapon = 0
        elif weapon == "main":
            weapon = 1
        elif weapon == "secondary":
            weapon = 2
        elif weapon == "everything":
            weapon = 3
        cmd = '{}testDisableWeaponMode {}'.format(self.console, weapon)
        self.write_command(cmd)
    
    @staticmethod
    def get_team(team):
        """
        Not a command for use manually! Converts parameter team given in the
        next commands to a number that can be understood from the server.
        :param team: "left", "right" or "spec"
        """
        if team == "left":
            return "0"
        elif team == "right":
            return "1"
        elif team == "spec":
            return "-1"

    def assign_team(self, nickname, team):
        """
        Moves target player to the given team when Tournament mode is off.
        :param nickname: Player's nickname to be moved
        :param team: "left", "right" or "spec"
        """
        cmd = '{}assignTeam "{}" {}'.format(self.console, Commands.aquote(nickname), Commands.get_team(team))
        self.write_command(cmd)

    def modify_tournament(self, nickname, team):
        """
        Moves target player to the given team when Tournament mode is on.
        :param nickname: Player's nickname to be moved
        :param team: "left", "right" or "spec"
        """
        cmd = '{}modifyTournament "{}" {}'.format(self.console, Commands.aquote(nickname), Commands.get_team(team))
        self.write_command(cmd)

    def assign_everyone(self, team):
        """
        Moves everyone in server to a single team when Tournament Mode is off.
        :param team: "left", "right" or "spec"
        """
        team_number = Commands.get_team(team)
        for player in self.players.all_nicknames():
            cmd = '{}assignTeam "{}" {}'.format(self.console, Commands.aquote(player), team_number)
            self.write_command(cmd)

    def modify_everyone(self, team):
        """
        Moves everyone in server to a single team when Tournament Mode is on.
        :param team: "left", "right" or "spec"
        """
        team_number = Commands.get_team(team)
        for player in self.players.all_nicknames():
            cmd = '{}modifyTournament "{}" {}'.format(self.console, Commands.aquote(player), team_number)
            self.write_command(cmd)
