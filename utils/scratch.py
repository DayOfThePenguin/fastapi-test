import requests
import wikipedia

from wikipedia.exceptions import PageError, DisambiguationError

WIKIURL = "https://en.wikipedia.org/w/api.php"


def search_title(title_guess):
    correct_title = None
    suggestions = []
    try:
        wikipedia.page(title_guess)
        correct_title = title_guess
    except:  # likely PageError or DisambiguationError
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
                # new_guess = json_data["query"]["searchinfo"]["suggestion"]
                suggestions = None
            else:  # add results to suggestions
                for page in json_data["query"]["search"]:
                    suggestions.append(page)
    return correct_title, suggestions


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
    links_complete = False
    plcontinue = None
    pllimit = num_links
    if num_links is None or num_links > 500:  # max allowed by mediawiki api
        pllimit = 500

    with requests.Session() as sess:
        while not links_complete:
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
            links = page[1]["links"]
            for link in links:
                if link["ns"] != 0:
                    print("skipped: {}".format(link["title"]))
                else:
                    pl.append(link["title"])
                    if len(pl) == num_links:
                        links_complete = True
            try:
                plcontinue = json_data["continue"]["plcontinue"]
                print("plcontinue: {}".format(plcontinue))
            except KeyError:
                links_complete = True
    return pl


if __name__ == "__main__":
    title_query = "python"
    TITLE, SUGGESTIONS = search_title(title_query)
    if SUGGESTIONS is None:
        msg = "The page {} does not exist.\n\nThere were no results matching the query"
        print(msg.format(title_query))
    elif TITLE is None:
        print("render page with suggestions as buttons")
        for suggestion in SUGGESTIONS:
            print(suggestion)
    else:
        LINKS = get_links(TITLE, num_links=15)
        print(LINKS)
        print("render map")
