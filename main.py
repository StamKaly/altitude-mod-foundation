from altitude import AltitudeMod


class ExampleMod(AltitudeMod):
    def on_client_add(self, player):
        self.commands.whisper(player.nickname, "Welcome to my server!")


if __name__ == '__main__':
    mod = ExampleMod(27275, '/home/user/altitude')
    mod.run()
