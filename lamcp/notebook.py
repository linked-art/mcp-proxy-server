from functools import lru_cache

# from lamcp.sources.nomisma.fetcher import NomismaFetcher
# from lamcp.sources.nomisma.mapper import NomismaMapper
from lamcp.sources.wikidata.fetcher import WikidataFetcher
from lamcp.sources.wikidata.mapper import WikidataMapper
from lamcp.sources.wikidata.searcher import WikidataSearcher
# from lamcp.sources.pleiades.fetcher import PleiadesFetcher
# from lamcp.sources.pleiades.mapper import PleiadesMapper


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
    #    "nomisma": {"fetcher": NomismaFetcher(cfg2), "mapper": NomismaMapper(cfg2)},
    #    "pleiades": {"fetcher": PleiadesFetcher(cfg3), "mapper": PleiadesMapper(cfg3)},
}

# configs["nomisma"]["mapper"].fetcher = configs["nomisma"]["fetcher"]
configs["wikidata"]["mapper"].fetcher = configs["wikidata"]["fetcher"]
# configs["pleiades"]["mapper"].fetcher = configs["pleiades"]["fetcher"]


# Query Wikidata by name
# https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&search=Alfred+Stieglitz&language=en

# Query Nomisma
# https://nomisma.org/feed/?q=type:%22nmo:Mint%22%20AND%20argos

# Query Pleaides
# Can't be done?

# getty
# select ?Subject ?Term ?Parents ?Descr ?ScopeNote ?Type (coalesce(?Type1,?Type2) as ?ExtraType) {
#  ?Subject luc:term "fishing* AND vessel*"; a ?typ.
#  ?typ rdfs:subClassOf gvp:Subject; rdfs:label ?Type.
#  filter (?typ != gvp:Subject)
#  optional {?Subject gvp:placeTypePreferred [gvp:prefLabelGVP [xl:literalForm ?Type1]]}
#  optional {?Subject gvp:agentTypePreferred [gvp:prefLabelGVP [xl:literalForm ?Type2]]}
#  optional {?Subject gvp:prefLabelGVP [xl:literalForm ?Term]}
#  optional {?Subject gvp:parentStringAbbrev ?Parents}
#  optional {?Subject foaf:focus/gvp:biographyPreferred/schema:description ?Descr}
#  optional {?Subject skos:scopeNote [dct:language gvp_lang:en; rdf:value ?ScopeNote]}
# }


# LUX
#


# Linked Art Constants
#
PRIMARY = "http://vocab.getty.edu/aat/300404670"


def get_primary_name(names):
    candidates = []
    for name in names:
        if name["type"] == "Name":
            langs = [x.get("equivalent", [{"id": None}])[0]["id"] for x in name.get("language", [])]
            cxns = [x.get("equivalent", [{"id": None}])[0]["id"] for x in name.get("classified_as", [])]
            if PRIMARY in cxns:
                return name
            else:
                candidates.append(name)

    candidates.sort(key=lambda x: len(x.get("language", [])), reverse=True)
    return candidates[0] if candidates else None


@lru_cache(maxsize=100)
def fetch_record(dataset, identifier, entity_type=""):
    """Fetch a record from the dataset and map to linked art"""

    if dataset not in configs:
        raise ValueError(f"Invalid dataset: {dataset}")
    fetcher = configs[dataset]["fetcher"]

    print(f"Fetching {identifier} from {dataset}")
    record = fetcher.fetch(identifier)
    return record


# @lru_cache(maxsize=100)
def map_record(dataset, record, entity_type):
    print(f"Mapping to LA...")
    mapper = configs[dataset]["mapper"]
    la = mapper.transform(record, entity_type)
    if la is not None:
        return la["data"]
    else:
        print(f"Failed to map from {dataset} to LA")
        return None


@lru_cache(maxsize=1000)
def make_simple_reference(dataset, identifier, entity_type=""):
    if identifier.startswith("http"):
        identifier = identifier.rsplit("/", 1)[-1]
    data = fetch_record(dataset, identifier, entity_type)
    rec = map_record(dataset, data, entity_type)
    if not rec:
        return None
    outrec = {}
    outrec["id"] = identifier
    outrec["type"] = rec["type"]
    outrec["name"] = get_primary_name(rec["identified_by"])["content"]
    return outrec, rec


def make_simple_record(dataset, uri, entity_type=""):
    try:
        outrec, rec = make_simple_reference(dataset, uri, entity_type)
    except Exception:
        return None
    if "classified_as" in rec:
        outrec["classifications"] = []
        for cxn in rec["classified_as"]:
            if "id" in cxn:
                try:
                    outrec["classifications"].append(make_simple_reference(dataset, cxn["id"])[0])
                except Exception:
                    continue
    if "referred_to_by" in rec:
        outrec["descriptions"] = []
        for stmt in rec["referred_to_by"]:
            if "language" in stmt:
                langs = [x.get("equivalent", [{"id": None}])[0]["id"] for x in stmt.get("language", [])]

            desc = {"content": stmt["content"]}
            if "classified_as" in stmt:
                desc["classifications"] = []
                for cxn in stmt["classified_as"]:
                    if "id" in cxn:
                        try:
                            desc["classifications"].append(make_simple_reference(dataset, cxn["id"])[0])
                        except Exception:
                            continue
            outrec["descriptions"].append(desc)
        # Arbitrarily limit descriptions to 5
        if len(outrec["descriptions"]) > 5:
            outrec["descriptions"] = outrec["descriptions"][:5]
    if "part_of" in rec:
        outrec["part_of"] = []
        for parent in rec["part_of"]:
            try:
                outrec["part_of"].append(make_simple_reference(dataset, parent["id"])[0])
            except Exception:
                continue
    elif "broader" in rec:
        outrec["part_of"] = []
        for parent in rec["broader"]:
            try:
                outrec["part_of"].append(make_simple_reference(dataset, parent["id"])[0])
            except Exception:
                continue
    if rec["type"] == "Person":
        if "born" in rec:
            # split into birthDate and birthPlace
            if "timespan" in rec["born"]:
                if "begin_of_the_begin" in rec["born"]["timespan"]:
                    outrec["birthDate"] = rec["born"]["timespan"]["begin_of_the_begin"]
            if "took_place_at" in rec["born"]:
                outrec["birthPlace"] = make_simple_reference(dataset, rec["born"]["took_place_at"][0]["id"])[0]
        if "died" in rec:
            # split into deathDate and deathPlace
            if "timespan" in rec["died"]:
                if "begin_of_the_begin" in rec["died"]["timespan"]:
                    outrec["deathDate"] = rec["died"]["timespan"]["begin_of_the_begin"]
            if "took_place_at" in rec["died"]:
                outrec["deathPlace"] = make_simple_reference(dataset, rec["died"]["took_place_at"][0]["id"])[0]
    elif rec["type"] == "Group":
        if "formed_by" in rec:
            # split into birthDate and birthPlace
            if "timespan" in rec["formed_by"]:
                if "begin_of_the_begin" in rec["formed_by"]["timespan"]:
                    outrec["foundingDate"] = rec["formed_by"]["timespan"]["begin_of_the_begin"]
            if "took_place_at" in rec["formed_by"]:
                outrec["foundingPlace"] = make_simple_reference(dataset, rec["formed_by"]["took_place_at"][0]["id"])[
                    0
                ]
            if "carried_out_by" in rec["formed_by"]:
                outrec["founder"] = [
                    make_simple_reference(dataset, x["id"])[0] for x in rec["formed_by"]["carried_out_by"]
                ]

        if "dissolved_by" in rec:
            # split into deathDate and deathPlace
            if "timespan" in rec["dissolved_by"]:
                if "begin_of_the_begin" in rec["dissolved_by"]["timespan"]:
                    outrec["dissolutionDate"] = rec["dissolved_by"]["timespan"]["begin_of_the_begin"]
            if "took_place_at" in rec["dissolved_by"]:
                outrec["dissolutionPlace"] = make_simple_reference(
                    dataset, rec["dissolved_by"]["took_place_at"][0]["id"]
                )[0]
            if "carried_out_by" in rec["dissolved_by"]:
                outrec["dissolver"] = make_simple_reference(dataset, rec["dissolved_by"]["carried_out_by"][0]["id"])[
                    0
                ]
    elif rec["type"] == "HumanMadeObject":
        # made_of
        # carries/shows -- embed this
        # ignore: dimensions, current_owner etc

        if "produced_by" in rec:
            cre = rec["produced_by"]
            if "timespan" in cre:
                dt = cre["timespan"].get("begin_of_the_begin", cre["timespan"].get("end_of_the_end", None))
                if dt is not None:
                    outrec["creationDate"] = dt
            if "took_place_at" in cre:
                outrec["creationPlace"] = make_simple_reference(dataset, cre["took_place_at"][0]["id"])[0]
            if "carried_out_by" in cre:
                outrec["creator"] = [make_simple_reference(dataset, x["id"])[0] for x in cre["carried_out_by"]]
            if "part" in cre:
                who = []
                for part in cre["part"]:
                    if "carried_out_by" in part:
                        who = [make_simple_reference(dataset, x["id"])[0] for x in part["carried_out_by"]]
                if "creator" in outrec:
                    outrec["creator"].extend(who)
                elif who:
                    outrec["creator"] = who

        if "encountered_by" in rec:
            cres = rec["encountered_by"]
            for cre in cres:
                if "timespan" in cre:
                    dt = cre["timespan"].get("begin_of_the_begin", cre["timespan"].get("end_of_the_end", None))
                    if dt is not None:
                        outrec["discoveryDate"] = dt
                if "took_place_at" in cre:
                    outrec["discoveryPlace"] = make_simple_reference(dataset, cre["took_place_at"][0]["id"])[0]
                if "carried_out_by" in cre:
                    outrec["discoverer"] = [make_simple_reference(dataset, x["id"])[0] for x in cre["carried_out_by"]]
                if "part" in cre:
                    who = []
                    for part in cre["part"]:
                        if "carried_out_by" in cre:
                            who = [make_simple_reference(dataset, x["id"])[0] for x in cre["carried_out_by"]]
                    if "discoverer" in outrec:
                        outrec["discoverer"].extend(who)
                    else:
                        outrec["discoverer"] = who

        if "made_of" in rec:
            outrec["material"] = [make_simple_reference(dataset, x["id"])[0] for x in rec["made_of"]]
        if "carries" in rec:
            outrec["carries"] = [make_simple_record(dataset, x["id"]) for x in rec["carries"]]
        if "shows" in rec:
            outrec["shows"] = [make_simple_record(dataset, x["id"]) for x in rec["shows"]]

    elif rec["type"] in ["LinguisticObject", "VisualItem"]:
        # about, represents
        # embed the HMO somehow? Would require a search...
        if "about" in rec:
            outrec["about"] = [make_simple_reference(dataset, x["id"])[0] for x in rec["about"]]
        if "represents" in rec:
            outrec["represents"] = [make_simple_reference(dataset, x["id"])[0] for x in rec["represents"]]

    if "member_of" in rec:
        outrec["member_of"] = []
        for parent in rec["member_of"]:
            try:
                outrec["member_of"].append(make_simple_reference(dataset, parent["id"])[0])
            except Exception:
                continue

    return outrec


def do_basic_name_search(datasets: str, entity_name: str, name_lang: str, entity_type: str):
    """
    Search for the top 20 entities in the given scope by their exact name.
    The `id` fields of references within the records can be used with the get_by_id tool to retrieve their full records.
    Use this tool to get started and then follow the identifiers to other records.

    Entity Types:
        - agent: People, organizations, etc.
        - place: Locations, cities, countries, etc.
        - concept: Concepts, ideas, etc.
        - set: Collections or sets of other entities, including items and sets

    Parameters:
        - dataset (str): The scope of the search. MUST be one of: item, work, agent, place, concept, set, event
        - entity_name (str): The name of the entity to search for
        - name_lang (str): The language of the name
        - entity_type (str): The type or class of entity

    Returns:
        - candidates (List[dict]): A list of candidate entity descriptions to choose from.
    """

    name = entity_name.lower()
    datasets = datasets.split(",")
    recs = []

    for ds in datasets:
        searcher = configs.get(ds, {}).get("searcher", None)
        if searcher is not None:
            # Here search for matches on name
            res = searcher.search(name, name_lang, entity_type)

            for uri in res["results"][:10]:
                outrec = make_simple_record(ds, uri, entity_type)
                if outrec is not None:
                    recs.append(outrec)

    return recs


def do_basic_fetch(dataset: str, identifier: str, entity_type: str):
    """
    Fetch a single entity by its identifier using `id` within a record, from a specific dataset

    Parameters:
        - dataset (str): The dataset to search within
        - identifier (str): The identifier of the entity to fetch

    Returns:
        - candidate (dict): The description of the entity, including links to other entities
    """
    identifier = str(identifier)
    print(f"Got: {dataset} , {identifier} , {entity_type}")
    outrec = make_simple_record(dataset, identifier, entity_type)
    return outrec
