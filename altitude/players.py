class Player:
    def __init__(self, nickname, vapor_id, player_id, ip):
        self.nickname = nickname
        self.vapor_id = vapor_id
        self.player_id = player_id
        self.ip = ip
        self.joined_after_change_map = True


class Players:
    def __init__(self, main_object, modded, lobby):
        self.main = main_object
        self.players = []
        self.modded = modded
        self.map_changed = False
        self.lobby = lobby
        self.commands = None

    def get_commands_object(self, commands_object):
        self.commands = commands_object

    def _on_map_change(self, map_name):
        self.map_changed = map_name
        if self.modded and self.players:
            for player in self.players:
                player.joined_after_change_map = False

    def _on_player_info_ev(self, player_id):
        if self.map_changed:
            for player in self.players:
                if player_id == player.player_id and not player.joined_after_change_map:
                    player.joined_after_change_map = True
                    self.main.on_player_map_change(player, self.map_changed)
                    return
            self.map_changed = False

    def check_nickname_existence(self, nickname):
        for player in self.players:
            if nickname == player.nickname:
                return True
        return False

    def get_all_players(self, nicknames, vapor_ids, player_ids, ips):
        players_list = [nicknames, vapor_ids, player_ids, ips]
        for count in range(len(nicknames)):
            self.players.append(Player(*[player[count] for player in players_list]))

    def add(self, nickname, vapor_id, player_id, ip):
        self.players.append(Player(nickname, vapor_id, player_id, ip))

    def remove(self, nickname):
        for player in self.players:
            if nickname == player.nickname:
                self.players.remove(player)
                break
        if self.lobby and len(self.players) == 0:
            self.commands.change_map(self.lobby)

    def nickname_change(self, old_nickname, new_nickname):
        for player in self.players:
            if old_nickname == player.nickname:
                player.nickname = new_nickname
                break

    def all_nicknames(self):
        return [player.nickname for player in self.players]

    def player_from_nickname(self, nickname):
        for player in self.players:
            if nickname == player.nickname:
                return player

    def player_from_vapor_id(self, vapor_id):
        for player in self.players:
            if vapor_id == player.vapor_id:
                return player

    def player_from_player_id(self, player_id):
        for player in self.players:
            if player_id == player.player_id:
                return player

    def get_all_vapor_ids(self):
        return [player.vapor_id for player in self.players]
