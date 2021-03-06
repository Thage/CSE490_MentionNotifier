from bs4 import BeautifulSoup
import urllib.parse, urllib.request, urllib.error
from urllib.parse import unquote, urlencode
from unidecode import unidecode
from re import match


"""
.. module:: GoogleSearchIter
    :platform: Windows
    :synopsis: holds the modified Google-Search-API by github.com user, abenassi. Holds the functions required in creating the GoogleResult objects used by our system.

"""


class GoogleResult(object):

    """Represents a google search result."""

    def __init__(self):
        self.name = None  # The title of the link
        self.link = None  # The external link
        self.description = None  # The description of the link
        self.page = None  # Results page this one was on
        self.index = None  # What index on this page it was on


    def __repr__(self):
        name = self._limit_str_size(self.name, 55)
        description = self._limit_str_size(self.description, 49)

        list_google = ["GoogleResult(",
                       "name={}".format(name), "\n", " " * 13,
                       "description={}".format(description)]

        return "".join(list_google)

    def _limit_str_size(self, str_element, size_limit):
        """Limit the characters of the string, adding .. at the end."""
        if not str_element:
            return None

        elif len(str_element) > size_limit:
            return unidecode(str_element[:size_limit]) + ".."

        else:
            return unidecode(str_element)


# PUBLIC

def GoogleResultGen(li,page,index):

    '''Aux function to be called for when creating a GoogleResult.'''
    res = GoogleResult()

    res.page = page
    res.index = index

    res.name = _get_name(li)
    res.link = _get_link(li)
    res.description = _get_description(li)
    return res

def dummy_func():
    '''Aux dummy function.'''
    pass




def search_iter(bundle, iterFunc=dummy_func(), pages=1, lang='en', void=True):
    """Returns a list of GoogleResult.

    :param str query: String to search in google.
    :param int pages: Number of pages where results must be taken.
    :returns: A GoogleResult object."""

    if pages == 0:
        pages = 30

    results = []
    for i in range(pages):
        url = _get_search_url(bundle.google_query, i, lang=lang)
        html = get_html(url)

        if html:
            soup = BeautifulSoup(html, "html.parser")
            divs = soup.findAll("div", attrs={"class": "g"})

            j = 0
            for li in divs:
                res = GoogleResultGen(li,i,j)
                if void is True:
                    if res.description is None:
                        continue
                iterFunc(res, bundle)
                results.append(res)
                j += 1
    print("Search end.")
    return results




# PRIVATE
def _get_name(li):
    """Return the name of a google search."""
    a = li.find("a")
    # return a.text.encode("utf-8").strip()
    if a is not None:
        return a.text.strip()
    return None


def _get_link(li):
    """Return external link from a search."""
    try:
        a = li.find("a")
        link = a["href"]
    except:
        return None

    if link.startswith("/url?"):
        m = match('/url\?(url|q)=(.+?)&', link)
        if m and len(m.groups()) == 2:
            return unquote(m.group(2))

    return None


def _get_description(li):
    '''Return the description of a google search.'''

    sdiv = li.find("div", attrs={"class": "s"})
    if sdiv:
        stspan = sdiv.find("span", attrs={"class": "st"})
        if stspan is not None:
            # return stspan.text.encode("utf-8").strip()
            return stspan.text.strip()
    else:
        return None


def get_html(url):
    header = "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101"
    try:
        request = urllib.request.Request(url)
        request.add_header("User-Agent", header)
        html = urllib.request.urlopen(request).read()
        return html
    except urllib.error.HTTPError as e:
        print("Error accessing:", url)
        if e.code == 503 and 'CaptchaRedirect' in e.read():
            print("Captcha Required.")
        return None
    except Exception as e:
        print("Error accessing:", url)
        print(e)
        return None

def _get_search_url(query, page=0, per_page=10, lang='en'):


    params = {'nl': lang, 'q': query.encode(
        'utf8'), 'start': page * per_page, 'num': per_page}
    params = urlencode(params)
    url = u"http://www.google.com/search?" + params

    return url