import logging
import re
import requests

logging.basicConfig(level=logging.INFO)
WIKIURL = "https://en.wikipedia.org/w/api.php"
cleanr = re.compile(r"<.*?>")


def cleanhtml(raw_html):
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext


def search_title(title_guess):
    suggestions = []
    with requests.Session() as sess:
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srlimit": "5",
            "srsearch": title_guess.replace(" ", "_"),
        }
        resp = sess.get(url=WIKIURL, params=params)
        json_data = resp.json()
        if json_data["query"]["searchinfo"]["totalhits"] == 0:  # no search results
            try:
                new_guess = json_data["query"]["searchinfo"]["suggestion"]
                suggestions = search_title(new_guess)  # if Wikipedia makes a guess
            except KeyError:  # if Wikipedia can't figure out what we tried to search for
                suggestions = None
        else:  # add results to suggestions
            for page in json_data["query"]["search"]:
                page["snippet"] = cleanhtml(page["snippet"])
                suggestions.append(page)

    return suggestions


def get_links(page_name, num_links=None):
    """fetch num_links links from a MediaWiki page.

    if num_links is None, get all links on the page. the mediawiki api supports
    requesting data for multiple pages at once, but this implementation will only
    get links for a single page at a time on a single thread to make sure we respect
    the Wikipedia servers and don't make too high volume requests (this is why
    json_data["query"]["pages"][0])

    Parameters
    ----------
    page_name : str
        name of the page (search for the page first and pass a known name to
        this function)
    num_links : int, optional
        how many links to get from the page, by default None (get all links)
    """
    pl = []
    plcontinue = None
    pllimit = num_links
    if num_links is None or num_links > 500:  # max allowed by mediawiki api
        pllimit = 500

    with requests.Session() as sess:
        while True:
            params = {
                "action": "query",
                "format": "json",
                "titles": page_name.replace(" ", "_"),
                "prop": "links",
                "pllimit": pllimit,
            }
            if plcontinue is not None:  # add the continue if this isn't the first loop
                params["plcontinue"] = plcontinue

            resp = sess.get(url=WIKIURL, params=params)
            json_data = resp.json()

            page = json_data["query"]["pages"].popitem()
            try:
                links = page[1]["links"]
            except KeyError:
                logging.error("Unable to get links for page %s", page_name)
                return pl  # will be empty list to fall through for loop
            for link in links:
                if link["ns"] == 0:
                    pl.append(link["title"])
                    if len(pl) == num_links:
                        return pl
            try:
                plcontinue = json_data["continue"]["plcontinue"]
                logging.info("%s plcontinue: %s", page_name, plcontinue)
            except KeyError:
                logging.info("%s has fewer links than %i", page_name, num_links)
                return pl


if __name__ == "__main__":
    title_query = "elon muskk"
    SUGGESTIONS = search_title(title_query)
    if SUGGESTIONS is None:
        msg = "The page {} does not exist.\n\nThere were no results matching the query"
        print(msg.format(title_query))
    else:
        print("render page with suggestions as buttons")
        for suggestion in SUGGESTIONS:
            print(suggestion)

    # TITLE = "Elon Musk"
    # LINKS = get_links(TITLE, num_links=15)
    # print(LINKS)
    # print("render map")
