from altitude import AltitudeMod


class SimpleMod(AltitudeMod):
    def on_client_add(self, player):
        self.commands.whisper(player.nickname, "Welcome to my server!")


if __name__ == '__main__':
    mod = SimpleMod(27275, '/home/user/altitude')
    mod.run()
