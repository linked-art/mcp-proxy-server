import requests


class Harvester:
    def __init__(self, config):
        self.endpoint = "https://collectionapi.metmuseum.org/public/collection/v1/objects"

    def harvest(self, from_time=None):
        # "https://collectionapi.metmuseum.org/public/collection/v1/objects?metadataDate=YYYY-MM-DD"
        # --> {"total": int, "objectIDs": List[int]}
        # if metadataDate, then only those modified since given date
        if from_time is not None:
            response = requests.get(self.endpoint, params={"metadataDate": from_time})
        else:
            response = requests.get(self.endpoint)
        response.raise_for_status()
        return response.json()["objectIDs"]
