import requests


class Searcher:
    def __init__(self, config):
        self.config = config
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def search(self, query, lang="", entity_type=""):
        # Implement base search logic here
        """Run the query and return URI results"""

        qurl = self.endpoint.format(QUERY=query, LANG=lang, ENTITY_TYPE=entity_type)
        resp = requests.get(qurl, headers=self.headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(f"Request failed with status code {resp.status_code}")
