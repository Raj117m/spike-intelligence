from pathlib import Path
import json


class Manifest:

    def __init__(self):

        self.file = Path("data_lake/history_manifest.json")

        self.file.parent.mkdir(parents=True, exist_ok=True)

        if not self.file.exists():

            self.file.write_text("{}")

    def load(self):

        return json.loads(self.file.read_text())

    def save(self, data):

        self.file.write_text(
            json.dumps(data, indent=2)
        )

    def completed(self, filename):

        return self.load().get(filename, False)

    def mark_complete(self, filename):

        data = self.load()

        data[filename] = True

        self.save(data)
