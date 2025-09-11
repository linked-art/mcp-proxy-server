import re
from cromulent import model, vocab
from lxml import etree

from .date_utils import make_datetime
import logging

logger = logging.getLogger("lux_pipeline")

model.ExternalResource._write_override = None
# monkey patch in members_exemplified_by for Set and Group
mebInfo = model.PropInfo("members_exemplified_by", "la:members_exemplified_by", model.CRMEntity, "", None, 1, 1)
model.Set._all_properties["members_exemplified_by"] = mebInfo
model.Group._all_properties["members_exemplified_by"] = mebInfo


class Mapper(object):
    def __init__(self, config):
        # Not sure if this is useful, but worth configuration once
        self.factory = model.factory
        self.factory.auto_assign_id = False
        self.factory.validate_properties = False
        self.factory.validate_profile = False
        self.factory.validate_range = False
        self.factory.validate_multiplicity = False
        self.factory.json_serializer = "fast"
        self.factory.order_json = False
        self.factory.cache_hierarchy()

        ### FIXME: How much of this is actually needed for *all* mappers?
        ### shouldn't they be instantiated on some constants instance
        ### and then referenced?

        self.process_langs = {}
        self.aat_material_ids = []
        self.aat_unit_ids = []
        for i in vocab.instances.values():
            if isinstance(i, model.Language):
                if hasattr(i, "notation"):
                    self.process_langs[i.notation] = i
            elif isinstance(i, model.Material):
                self.aat_material_ids.append(i.id)
            elif isinstance(i, model.MeasurementUnit):
                self.aat_unit_ids.append(i.id)

        self.lang_three_to_two = {
            "por": "pt",
            "deu": "de",
            "ger": "de",
            "eng": "en",
            "fra": "fr",
            "fre": "fr",
            "spa": "es",
            "zho": "zh",
            "chi": "zh",
            "hin": "hi",
            "afr": "af",
            "alb": "sq",
            "sqi": "sq",
            "ara": "ar",
            "bul": "bg",
            "bos": "bs",
            "cat": "ca",
            "ben": "bn",
            "rus": "ru",
            "nld": "nl",
            "dut": "nl",
            "fin": "fi",
            "ile": "is",
            "gle": "ga",
            "ita": "it",
            "fas": "fa",
            "per": "fa",
            "guj": "gu",
            "kor": "ko",
            "lat": "la",
            "lit": "lt",
            "mac": "mk",
            "mkd": "mk",
            "jpn": "ja",
            "hrv": "hr",
            "ces": "cs",
            "cze": "cs",
            "dan": "da",
            "ell": "el",
            "gre": "el",
            "kat": "ka",
            "geo": "ka",
            "heb": "he",
            "hun": "hu",
            "nor": "no",
            "pol": "pl",
            "ron": "ro",
            "rum": "ro",
            "slk": "sk",
            "slo": "sk",
            "slv": "sl",
            "srp": "sr",
            "swe": "sv",
            "tur": "tr",
            "cym": "cy",
            "wel": "cy",
            "urd": "ur",
            "swa": "sw",
            "ind": "id",
            "tel": "te",
            "tam": "ta",
            "tha": "th",
            "mar": "mr",
            "pan": "pa",
        }

        self.must_have = ["en", "es", "fr", "pt", "de", "nl", "zh", "ja", "ar", "hi"]

        self.config = config

        # Mapping might need preferred URI for source
        self.namespace = config["namespace"]
        self.name = config["name"]
        self.debug = False
        self.acquirer = None

        self.single_century_regex = re.compile(
            r"(early|mid|late)?\s*(\d{1,2})(?:st|nd|rd|th) century$", re.IGNORECASE
        )
        self.range_centuries_regex = re.compile(
            r"(early|mid|late)?\s*(\d{1,2})(?:st|nd|rd|th) century\s*-\s*(early|mid|late)?\s*(\d{1,2})(?:st|nd|rd|th) century",
            re.IGNORECASE,
        )

    def make_export_filename(self, name, my_slice):
        return f"export_{name}_{my_slice}.jsonl"

    def returns_multiple(self, record=None):
        return False

    def should_merge_into(self, base, merge):
        return True

    def should_merge_from(self, base, merge):
        return True

    def fix_identifier(self, identifier):
        return identifier

    def expand_uri(self, identifier):
        return self.namespace + identifier

    def to_plain_string(self, value):
        return str(value) if isinstance(value, etree._ElementUnicodeResult) else value

    def extract_index_data(self, data):
        # From the raw data, extract fields for indexing
        # default fields:  label, equiv, diff
        return {}

    def get_reference(self, identifier):
        try:
            fdata = self.fetcher.fetch(identifier)
            frec = self.transform(fdata, reference=True)
        except:
            raise
            return None

        if frec is not None:
            rectype = frec["data"]["type"]
            crmcls = getattr(model, rectype)
            return crmcls(ident=self.expand_uri(identifier), label=frec["data"].get("_label", ""))
        else:
            return None

    def post_mapping(self, record, xformtype=None):
        return record

    def transform(self, record, rectype, reference=False):
        # No op
        # This almost certainly needs to be overridden
        return record


class MultiMapper(Mapper):
    # A mapper that will return a list of extracted records via transform_all
    # Or only the "main" record via transform

    def returns_multiple(self, record=None):
        return True

    def transform_all(self, record):
        return [record]
