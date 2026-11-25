from dataclasses import dataclass


@dataclass(slots=True)
class Source:

    id: str

    name: str

    homepage: str

    download_url: str

    update_frequency: str

    format: str

    storage_folder: str

    enabled: bool = True
