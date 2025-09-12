from ..base.searcher import Searcher


class WikidataSearcher(Searcher):
    def __init__(self, config):
        super().__init__(config)
        self.endpoint = (
            "https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&search={QUERY}&language={LANG}"
        )

    def search(self, query, lang="", entity_type=""):
        # Implement search logic here
        results = super().search(query, lang, entity_type)
        ids = {}
        for hit in results["search"]:
            if not hit["id"] in ids:
                ids[hit["id"]] = hit
        return {"results": list(ids.keys())}
