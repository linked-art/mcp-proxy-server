from ..base.fetcher import Fetcher


# just works
class PleiadesFetcher(Fetcher):
    def validate_identifier(self, identifier):
        return True
