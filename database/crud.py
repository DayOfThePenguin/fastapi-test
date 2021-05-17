import wikipedia

from database.models import WikiMap


def get_search_result(title: str) -> str:
    return wikipedia.page(title)
