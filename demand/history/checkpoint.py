from pathlib import Path


class Checkpoint:

    def __init__(self):

        self.path = Path("data_lake/history_checkpoint.txt")

    def save(self, value):

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path.write_text(str(value))

    def load(self):

        if not self.path.exists():

            return ""

        return self.path.read_text().strip()
