from ..base.searcher import Searcher
from urllib.parse import urlencode
import json
import requests


class LuxSearcher(Searcher):
    def __init__(self, config):
        super().__init__(config)
        self.endpoint = "https://lux.collections.yale.edu/api/search/"

    def search(self, query, lang="", entity_type=""):
        if entity_type in ["Person", "Group"]:
            qurl = self.endpoint + "agent?"
            if entity_type == "Person":
                q = {"AND": [{"recordType": "person"}, {"name": query}]}
            elif entity_type == "Group":
                q = {"AND": [{"recordType": "group"}, {"name": query}]}
        elif entity_type == "Place":
            qurl = self.endpoint + "place?"
            q = {"AND": [{"name": query}]}

        qec = urlencode({"q": json.dumps(q)})
        qurl += qec
        resp = requests.get(qurl, headers=self.headers)

        recs = []

        if resp.status_code == 200:
            js = resp.json()
            for entry in js["orderedItems"]:
                recs.append(entry["id"])
            return {"results": recs}
        else:
            print(resp.text)
            raise Exception(f"Request failed with status code {resp.status_code}")
