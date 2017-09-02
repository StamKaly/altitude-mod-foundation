import sqlite3


class BotDatabase:
    def __init__(self):
        self.connection = sqlite3.connect('alti_discord.database')
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS AltiDiscord(vaporId TEXT, discordId TEXT)")
        self.connection.commit()

    def add(self, vapor_id, discord_id):
        self.cursor.execute("INSERT INTO AltiDiscord VALUES(?, ?)", (vapor_id, discord_id,))
        self.connection.commit()

    def check_if_registered(self, vapor_id):
        for user in self.cursor.execute("SELECT 1 FROM AltiDiscord WHERE vaporId = ?", (vapor_id,)):
            if user == (1,):
                return True
        return False

    def check_if_in_channel(self, vapor_id, discord_ids):
        self.cursor.execute("SELECT vaporId, discordId FROM AltiDiscord")
        for user in self.cursor.fetchall():
            if user[0] == vapor_id and user[1] in discord_ids:
                return user[1]

    def get_in_channel(self, vapor_ids, discord_ids):
        self.cursor.execute("SELECT vaporId, discordId FROM AltiDiscord")
        users = []
        for user in self.cursor.fetchall():
            if user[0] in vapor_ids and user[1] in discord_ids:
                users.append(user[0])
        return users
