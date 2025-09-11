from ..base.fetcher import Fetcher


# works
class PleiadesFetcher(Fetcher):
    def validate_identifier(self, identifier):
        return True
