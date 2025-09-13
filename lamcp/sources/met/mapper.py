from ..base.mapper import Mapper
from ..base.date_utils import make_datetime
from cromulent import model, vocab

example = {
    "objectID": 438003,
    "accessionNumber": "2002.62.1",
    "accessionYear": "2002",
    "primaryImage": "",
    "primaryImageSmall": "",
    "additionalImages": [],
    "constituents": [
        {
            "constituentID": 162135,
            "role": "Artist",
            "name": "Claude Monet",
            "constituentULAN_URL": "http://vocab.getty.edu/page/ulan/500019484",
            "constituentWikidata_URL": "https://www.wikidata.org/wiki/Q296",
            "gender": "",
        }
    ],
    "department": "European Paintings",
    "objectName": "Painting",
    "title": "Camille Monet (1847–1879) on a Garden Bench",
    "culture": "",
    "period": "",
    "dynasty": "",
    "reign": "",
    "portfolio": "",
    "artistRole": "Artist",
    "artistPrefix": "",
    "artistDisplayName": "Claude Monet",
    "artistDisplayBio": "French, Paris 1840–1926 Giverny",
    "artistSuffix": "",
    "artistAlphaSort": "Monet, Claude",
    "artistNationality": "French",
    "artistBeginDate": "1840",
    "artistEndDate": "1926",
    "artistGender": "",
    "artistWikidata_URL": "https://www.wikidata.org/wiki/Q296",
    "artistULAN_URL": "http://vocab.getty.edu/page/ulan/500019484",
    "objectDate": "1873",
    "objectBeginDate": 1873,
    "objectEndDate": 1873,
    "medium": "Oil on canvas",
    "dimensions": "23 7/8 x 31 5/8 in. (60.6 x 80.3 cm)",
    "measurements": [
        {
            "elementName": "Framed",
            "elementDescription": None,
            "elementMeasurements": {"Depth": 11.430023, "Height": 88.90018, "Width": 109.220215},
        },
        {
            "elementName": "Overall",
            "elementDescription": None,
            "elementMeasurements": {"Height": 60.6, "Width": 80.3},
        },
    ],
    "creditLine": "The Walter H. and Leonore Annenberg Collection, Gift of Walter H. and Leonore Annenberg, 2002, Bequest of Walter H. Annenberg, 2002",
    "geographyType": "",
    "city": "",
    "state": "",
    "county": "",
    "country": "",
    "region": "",
    "subregion": "",
    "locale": "",
    "locus": "",
    "excavation": "",
    "river": "",
    "classification": "Paintings",
    "rightsAndReproduction": "",
    "linkResource": "",
    "metadataDate": "2025-07-02T04:50:13.22Z",
    "repository": "Metropolitan Museum of Art, New York, NY",
    "objectURL": "https://www.metmuseum.org/art/collection/search/438003",
    "tags": [
        {
            "term": "Gardens",
            "AAT_URL": "http://vocab.getty.edu/page/aat/300008090",
            "Wikidata_URL": "https://www.wikidata.org/wiki/Q1107656",
        },
        {
            "term": "Men",
            "AAT_URL": "http://vocab.getty.edu/page/aat/300025928",
            "Wikidata_URL": "https://www.wikidata.org/wiki/Q8441",
        },
        {
            "term": "Women",
            "AAT_URL": "http://vocab.getty.edu/page/aat/300025943",
            "Wikidata_URL": "https://www.wikidata.org/wiki/Q467",
        },
        {
            "term": "Benches",
            "AAT_URL": "http://vocab.getty.edu/page/aat/300038494",
            "Wikidata_URL": "https://www.wikidata.org/wiki/Q204776",
        },
    ],
    "objectWikidata_URL": "https://www.wikidata.org/wiki/Q13451237",
    "isTimelineWork": None,
    "GalleryNumber": "821",
}


class MetMapper(Mapper):
    def __init__(self, config):
        config["name"] = "met"
        config["namespace"] = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"
        Mapper.__init__(self, config)
        self.classification_lookup = {"Painting": vocab.Painting, "Coins": vocab.Coin}

    def guess_type(self, record):
        return model.HumanMadeObject

    def canonicalize(self, uri):
        if "vocab.getty.edu" in uri:
            return uri.replace("/page", "")
        elif "wikidata" in uri:
            # Should be entity, not human wiki page
            qid = uri.rsplit("/", 1)[1]
            return f"http://www.wikidata.org/entity/{qid}"
        else:
            return uri

    def transform(self, record, recordType="HumanMadeObject", reference=False):
        # Should probably be a multi-mapper as artists
        # are inlined in the response, and we'll need the VI as well as the HMO

        data = record["data"]
        myid = data["objectID"]
        title = data["title"]
        cxn = data.get("classification", data.get("objectName", ""))
        cls = self.classification_lookup.get(cxn, model.HumanMadeObject)
        item = cls(ident=self.namespace + str(myid), label=title)
        item.identified_by = vocab.PrimaryName(content=title)
        item.identified_by = vocab.AccessionNumber(content=data["accessionNumber"])
        item.identified_by = vocab.LocalNumber(content=str(data["objectID"]))

        # Descriptions

        if medium := data["medium"]:
            item.referred_to_by = vocab.MaterialStatement(content=medium)
        if dims := data["dimensions"]:
            item.referred_to_by = vocab.DimensionStatement(content=dims)
        if credit := data["creditLine"]:
            item.referred_to_by = vocab.CreditStatement(content=credit)

        # Dimensions

        for dims in data["measurements"]:
            if dims["elementName"] == "Overall":
                if h := dims["elementMeasurements"].get("Height", None):
                    item.dimension = vocab.Height(value=h)
                if w := dims["elementMeasurements"].get("Width", None):
                    item.dimension = vocab.Width(value=w)
                if d := dims["elementMeasurements"].get("Depth", None):
                    item.dimension = vocab.Depth(value=d)
                for i in item.dimension:
                    i.unit = vocab.instances["cm"]

        # Equivalent
        if eq := data.get("objectWikidata_URL", None):
            item.equivalent = model.HumanMadeObject(ident=self.canonicalize(eq), label=title)

        # Images
        if img := data.get("primaryImage", None):
            vi = model.VisualItem(label="Main Image")
            do = vocab.DigitalImage(label="Main Image File")
            do.access_point = model.DigitalObject(ident=img)
            item.representation = vi

        # Production

        prod = model.Production()

        ts = model.TimeSpan()
        if obd := data.get("objectBeginDate", None) is not None:
            ts.begin_of_the_begin = f"{obd}-01-01T00:00:00"
        if oed := data.get("objectEndDate", None) is not None:
            ts.end_of_the_end = f"{oed}-12-31T23:59:59"
        if od := data.get("objectDate", None) is not None:
            ts.identified_by = vocab.DisplayName(content=od)
            if not obd and not oed:
                # parse string date
                try:
                    b, e = make_datetime(od)
                    ts.begin_of_the_begin = b
                    ts.end_of_the_end = e
                except Exception as e:
                    print(f"Couldn't parse date string: {od}")
        if obd or oed or od:
            prod.timespan = ts

        # Artist
        if aname := data.get("artistDisplayName", None):
            wd = data.get("artistWikidata_URL", None)
            ulan = data.get("artistULAN_URL", None)
            ident = ulan if ulan else wd
            if ident is None:
                # FIXME: Local artist, needs reconciling
                artist = model.Person(label=aname)
            else:
                artist = model.Person(ident=self.canonicalize(ident), label=aname)
            prod.carried_out_by = artist

        if period := data.get("period", ""):
            # Would need reconciling...
            prod.during = model.Period(label=period)

        # if geographyType implies production location, add took_place_at

        if aname or obd or oed or od:
            item.produced_by = prod

        if gn := data.get("GalleryNumber", ""):
            # No gallery information API
            gid = self.namespace + f"gallery/{gn}"
            item.current_location = vocab.Gallery(ident=gid, name=gn)

        if "tags" in data:
            vi = model.VisualItem(ident=self.namespace + f"vi/{myid}")
            for tag in data["tags"]:
                aat = tag.get("AAT_URL", None)
                wd = tag.get("Wikidata_URL", None)
                tagid = aat if aat else wd
                if tagid is not None:
                    vi.about = model.Type(ident=self.canonicalize(tagid), label=tag["term"])
            item.shows = vi

        data = model.factory.toJSON(item)
        return {"data": data, "identifier": str(myid), "source": "met"}
