import duckdb


class ReplayDatabase:

    def __init__(self):

        self.con = duckdb.connect("data/demand.duckdb")
