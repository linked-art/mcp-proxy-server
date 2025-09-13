import requests


class Fetcher:
    def __init__(self, config):
        self.endpoint = "https://collectionapi.metmuseum.org/public/collection/v1/objects/{identifier}"

    def fetch(self, identifier):
        # "https://collectionapi.metmuseum.org/public/collection/v1/objects/nnnnnn"
        # --> {custom json format}
        response = requests.get(self.endpoint.format({"identifier": identifier}))
        response.raise_for_status()
        return {"data": response.json(), "source": "met"}
