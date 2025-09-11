from .nomisma.fetcher import NomismaFetcher
from .nomisma.mapper import NomismaMapper
from .wikidata.fetcher import WikidataFetcher
from .wikidata.mapper import WikidataMapper
from .wikidata.searcher import WikidataSearcher
from .pleiades.fetcher import PleiadesFetcher
from .pleiades.mapper import PleiadesMapper


cfg = {
    "name": "wikidata",
    "type": "external",
    "namespace": "http://www.wikidata.org/entity/",
    "matches": ["wikidata.org/entity/", "wikidata.org/wiki/"],
    "fetch": "https://www.wikidata.org/wiki/Special:EntityData/{identifier}.json",
}


cfg2 = {
    "name": "nomisma",
    "type": "external",
    "namespace": "http://nomisma.org/id/",
    "matches": ["nomisma.org"],
    "fetch": "http://nomisma.org/id/{identifier}.jsonld",
}


cfg3 = {
    "name": "pleiades",
    "type": "external",
    "namespace": "https://pleiades.stoa.org/places/",
    "matches": ["pleiades.stoa.org"],
    "fetch": "https://pleiades.stoa.org/places/{identifier}/json",
    "wikidata_property": ["P950"],
}


configs = {
    "wikidata": {"fetcher": WikidataFetcher(cfg), "mapper": WikidataMapper(cfg), "searcher": WikidataSearcher(cfg)},
    "nomisma": {"fetcher": NomismaFetcher(cfg2), "mapper": NomismaMapper(cfg2)},
    "pleiades": {"fetcher": PleiadesFetcher(cfg3), "mapper": PleiadesMapper(cfg3)},
}

configs["nomisma"]["mapper"].fetcher = configs["nomisma"]["fetcher"]
configs["wikidata"]["mapper"].fetcher = configs["wikidata"]["fetcher"]
configs["pleiades"]["mapper"].fetcher = configs["pleiades"]["fetcher"]
