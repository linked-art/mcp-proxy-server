from ..base.searcher import Searcher

x = {
    "searchinfo": {"search": "alfred stieglitz"},
    "search": [
        {
            "id": "Q313055",
            "title": "Q313055",
            "pageid": 301104,
            "concepturi": "http://www.wikidata.org/entity/Q313055",
            "repository": "wikidata",
            "url": "//www.wikidata.org/wiki/Q313055",
            "display": {
                "label": {"value": "Alfred Stieglitz", "language": "en"},
                "description": {"value": "American photographer (1864–1946)", "language": "en"},
            },
            "label": "Alfred Stieglitz",
            "description": "American photographer (1864–1946)",
            "match": {"type": "label", "language": "en", "text": "Alfred Stieglitz"},
        }
    ],
    "search-continue": 7,
    "success": 1,
}


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
