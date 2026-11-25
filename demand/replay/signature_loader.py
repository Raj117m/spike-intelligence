from demand.replay.database import ReplayDatabase


class SignatureLoader:

    def __init__(self):

        self.db = ReplayDatabase()

    def load(self):

        return self.db.con.execute(
            """
            SELECT *
            FROM signatures
            """
        ).fetchdf()
