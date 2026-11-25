from demand.acquisition.adapters.base import DatasetAdapter


class AdapterFactory:

    _registry = {}

    @classmethod
    def register(cls, name: str, adapter: type[DatasetAdapter]):
        cls._registry[name] = adapter

    @classmethod
    def create(cls, name: str) -> DatasetAdapter:

        if name not in cls._registry:
            raise KeyError(name)

        return cls._registry[name]()
