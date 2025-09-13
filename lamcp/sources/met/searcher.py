import requests


class Searcher:
    def __init__(self, config):
        self.endpoint = "https://collectionapi.metmuseum.org/public/collection/v1/search"

    def harvest(self, q):
        # "https://collectionapi.metmuseum.org/public/collection/v1/objects?metadataDate=YYYY-MM-DD"
        # --> {"total": int, "objectIDs": List[int]}
        # if metadataDate, then only those modified since given date
        response = requests.get(self.endpoint, params={"q": q})
        response.raise_for_status()
        return response.json()["objectIDs"]
