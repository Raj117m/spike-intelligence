from demand.providers.engine import ProviderEngine
from demand.providers.wikidata import WikidataProvider


class EntityLinker:

    def __init__(self):

        self.engine = ProviderEngine(WikidataProvider())

    def link(self, row):

        query = f"{row['title']} {row['categoryName']}"

        results = self.engine.search(query)

        return results
