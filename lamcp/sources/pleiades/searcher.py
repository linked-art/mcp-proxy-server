from ..base.searcher import Searcher
from lxml import etree
import requests


# https://pleiades.stoa.org/search_rss?portal_type%3Alist=Place&review_state%3Alist=published&Title=Zucchabar


class PleiadesSearcher(Searcher):
    def __init__(self, config):
        super().__init__(config)
        self.endpoint = "https://pleiades.stoa.org/search_rss?portal_type%3Alist=Place&review_state%3Alist=published&Title={QUERY}"

    def search(self, query, lang="", entity_type=""):
        qurl = self.endpoint.format(QUERY=query, LANG=lang, ENTITY_TYPE=entity_type)
        resp = requests.get(qurl, headers=self.headers)
        if resp.status_code == 200:
            data = resp.text
        else:
            raise Exception(f"Request failed with status code {resp.status_code}")

        data = data.encode("utf-8")
        dom = etree.XML(data)

        # xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        # xmlns="http://purl.org/rss/1.0/"
        # item xpath: /rdf:RDF/channel/items/rdf:Seq/rdf:li/@rdf:resource
        nss = {"rss": "http://purl.org/rss/1.0/", "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}
        recs = []
        items = dom.xpath("/rdf:RDF/rss:channel/rss:items/rdf:Seq/rdf:li/@rdf:resource", namespaces=nss)
        for item in items:
            recs.append(str(item))
        return {"results": recs}
