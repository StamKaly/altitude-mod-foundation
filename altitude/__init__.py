from . import commands, players
from os.path import getsize, join, isfile
from os import remove
import json
import time


def teamno_to_team_colour(team_number):
    colours = [2, 'Spec',
               3, 'Red',
               4, 'Blue',
               5, 'Green',
               6, 'Yellow',
               7, 'Orange',
               8, 'Purple',
               9, 'Azure',
               10, 'Pink',
               11, 'Brown']
    for number in colours:
        if team_number == number:
            return colours[colours.index(number) + 1]


class AltitudeMod:
    def __init__(self, port, altitude_path, modded=False, lobby=None):
        self.log_file = join(altitude_path, 'servers', 'log.txt')
        self.old_log_file = join(altitude_path, 'servers', 'log_old.txt')
        self.archive_log_file = join(altitude_path, 'servers', 'log_archive.txt')
        self.players = players.Players(self, modded, lobby)
        self.commands = commands.Commands(self.players, port, join(altitude_path, 'servers', 'command.txt'))
        self.players.get_commands_object(self.commands)
        self.current_line = 0

    def parse(self, decoded):
        try:
            event = decoded['type']
            if event == "chat":
                self.on_chat(self.players.player_from_player_id(decoded['player']),
                             *[decoded[argument] for argument in ['message', 'server', 'team']])
            elif event == "mapChange":
                self.players._on_map_change(decoded['map'])
                self.on_server_map_change(decoded['map'], decoded['mode'],
                                          *[teamno_to_team_colour(decoded['{}Team'.format(team)])
                                            for team in ['right', 'left']])
            elif event == "logPlanePositions":
                position_by_player = []
                for player in decoded['positionByPlayer']:
                    position_by_player.append([self.players.player_from_player_id(player),
                                               tuple(decoded['positionByPlayer'][player].split(','))])
                self.on_log_plane_positions(position_by_player)
            elif event == "goal":
                scorer = self.players.player_from_player_id(decoded['player'])
                assister = None if decoded['assister'] < 0 else \
                    self.players.player_from_player_id(decoded['assister'])
                secondary_assister = None if decoded['secondaryAssister'] < 0 else \
                    self.players.player_from_player_id(decoded['secondaryAssister'])
                self.on_goal(scorer, assister, secondary_assister, decoded['xp'])
            elif event == "structureDestroy":
                self.on_structure_destroy(self.players.player_from_player_id(decoded['player']), decoded['target'],
                                          decoded['xp'])
            elif event == "kill":
                kill_type = "crash" if decoded['source'] == "plane" and decoded['player'] == -1 else "turret_kill" \
                    if decoded['source'] == "turret" else "plane_kill"
                killer = self.players.player_from_player_id(decoded['player']) if kill_type == "plane_kill" else None
                self.on_kill(kill_type, killer, self.players.player_from_player_id(decoded['victim']),
                             decoded['multi'], decoded['streak'])
            elif event == "roundEnd":
                # TODO: parse everything given
                # {"port":27279,"participantStatsByName":{"Crashes":[1,2,0],"Kills":[3,1,0],"Longest Life":[216,158,0],
                # "Ball Possession Time":[0,0,0],"Goals Scored":[0,0,0],"Damage Received":[700,1120,0],
                # "Assists":[0,0,0],"Experience":[75,25,0],"Damage Dealt":[340,510,0],"Goals Assisted":[0,0,0],
                # "Damage Dealt to Enemy Buildings":[0,0,0],"Deaths":[2,5,0],"Multikill":[0,0,0],"Kill Streak":[2,1,0]},
                # "winnerByAward":{"Most Helpful":0,"Best Kill Streak":0,"Longest Life":0,"Most Deadly":0,
                # "Best Multikill":0},"time":441083559,"type":"roundEnd","participants":[0,1,2]}
                self.on_round_end()
            elif event == "consoleCommandExecute":
                if decoded['source'] != "00000000-0000-0000-0000-000000000000":
                    self.on_command(self.players.player_from_vapor_id(decoded['source']),
                                    *[decoded[argument] for argument in ['command', 'arguments', 'group']])
            elif event == "clientAdd":
                self.players.add(*[decoded[argument] for argument in ['nickname', 'vaporId', 'player']],
                                 decoded['ip'].split(":")[0])
                self.on_client_add(self.players.player_from_player_id(decoded['player']))
            elif event == "logServerStatus":
                self.players.get_all_players(*[decoded[argument] for argument in ['nicknames', 'vaporIds',
                                                                                  'playerIds']],
                                             [ip.split(':')[0] for ip in decoded['ips']])
            elif event == "clientRemove":
                self.players.remove(decoded['nickname'])
                self.on_client_remove(decoded['nickname'], decoded['vaporId'], decoded['ip'].split(':')[0],
                                      decoded['reason'])
            elif event == "clientNicknameChange":
                self.players.nickname_change(decoded['oldNickname'], decoded['newNickname'])
                self.on_nickname_change(decoded['oldNickname'],
                                        self.players.player_from_nickname(decoded['newNickname']))
            elif event == "playerInfoEv":
                self.players._on_player_info_ev(decoded['player'])
            elif event == "spawn":
                self.on_spawn(self.players.player_from_player_id(decoded['player']),
                              *[decoded[argument] for argument in ['plane', 'perkRed', 'perkGreen',
                                                                   'perkBlue', 'skin']],
                              teamno_to_team_colour(decoded['team']))
        except KeyError:
            print('Could not handle line "{}"'.format(decoded))

    def archive_log(self):
        with open(self.log_file) as log:
            with open(self.archive_log_file, "a") as archive:
                archive.write(log.read())
        with open(self.log_file, "w"):
            pass

    def _run_on_every_loop(self):
        pass

    def run(self):
        if getsize(self.log_file) != 0:
            self.archive_log()
        self.commands.log_server_status()
        while True:
            with open(self.log_file) as log:
                for line in log.readlines()[self.current_line:]:
                    if 'port' in line:
                        try:
                            self.parse(json.loads(line))
                        except json.decoder.JSONDecodeError:
                            print("JSON error -- could not parse line {}".format(line))
                        finally:
                            self.current_line += 1
                            if isfile(self.old_log_file):
                                self.current_line = 0
                                with open(self.old_log_file) as old_log_file:
                                    with open(self.archive_log_file, "a") as archive:
                                        archive.writelines(old_log_file.readlines())
                                remove(self.old_log_file)
            self._run_on_every_loop()
            time.sleep(0.01)

    def on_chat(self, player, message, server_message, team_message):
        pass

    def on_server_map_change(self, map_name, mode, right_team, left_team):
        pass

    def on_player_map_change(self, player, map_name):
        pass

    def on_log_plane_positions(self, position_by_player):
        pass

    def on_goal(self, scorer, assister, secondary_assister, xp):
        pass

    def on_structure_destroy(self, player, target, xp):
        pass

    def on_kill(self, kill_type, killer, victim, multikill, streak):
        pass

    def on_round_end(self):
        pass

    def on_command(self, player, command_name, arguments, group):
        pass

    def on_client_add(self, player):
        pass

    def on_client_remove(self, nickname, vapor_id, ip, reason):
        pass

    def on_nickname_change(self, old_nickname, player):
        pass

    def on_spawn(self, player, plane, red_perk, green_perk, blue_perk, skin, team):
        pass
