from ..base.searcher import Searcher
from SPARQLWrapper import SPARQLWrapper, JSON

q = """
select ?Subject {
  ?Subject luc:term "Monet"; a gvp:PersonConcept .
}
"""
# -->
res = {
    "head": {"vars": ["subject"]},
    "results": {
        "bindings": [
            {"subject": {"type": "uri", "value": "http://vocab.getty.edu/ulan/500019484"}},
            {"subject": {"type": "uri", "value": "http://vocab.getty.edu/ulan/500191427"}},
            {"subject": {"type": "uri", "value": "http://vocab.getty.edu/ulan/500110191"}},
            {"subject": {"type": "uri", "value": "http://vocab.getty.edu/ulan/500341121"}},
            {"subject": {"type": "uri", "value": "http://vocab.getty.edu/ulan/500003469"}},
            {"subject": {"type": "uri", "value": "http://vocab.getty.edu/ulan/500122137"}},
            {"subject": {"type": "uri", "value": "http://vocab.getty.edu/ulan/500016714"}},
        ]
    },
}


class GettySearcher(Searcher):
    def __init__(self, config):
        Searcher.__init__(self, config)

    def search(self, query, lang, entity_type):
        # Implement search logic here
        ets = {"Person": "gvp:PersonConcept", "Group": "gvp:GroupConcept", "Place": "gvp:PlaceConcept"}
        q = 'SELECT ?subject WHERE { ?subject luc:term "' + query + f'" ; a {ets[entity_type]} . }}'

        sparql = SPARQLWrapper("http://vocab.getty.edu/sparql/")
        sparql.setReturnFormat(JSON)
        sparql.setQuery(q)
        res = sparql.query().convert()
        results = []
        for item in res["results"]["bindings"]:
            results.append(item["subject"]["value"])
        return {"results": results}
