from collections import OrderedDict

try:
    from urllib.parse import urlunparse
    from urllib.parse import urlparse
    from urllib.parse import quote_plus
    from .ezurllib import urlencode
except ImportError:
    from urlparse import urlunparse
    from urlparse import urlparse
    from urllib import quote_plus
    from .ezurllib import urlencode



class Url(object):

    """
    This class allows more flexible generation of URLS.
    This prevents the mindless manipulation string that occur
    in projects that require generation of a wide range of urls

    """

    def __init__(self, hostname, scheme="https", querydelimiter="&"):
        """
        Initializes the Url object

        :param hostname: The hostname of the Url
        :param scheme: Optional Scheme selection. Defaults to https
        :param querydelimiter: What the query delimiter is for this URL

        """
        self.__safe__ = "+"
        self.__scheme__ = scheme
        self.__hostname__ = hostname
        self.__pages__ = list()
        self.__query__ = OrderedDict()
        self.__fragment__ = ""
        self.__querydelimiter__ = querydelimiter

    def __repr__(self):
        """REPR Implementation"""
        return "<url:{url}>".format(url=str(self))

    @property
    def url(self):
        return urlparse(str(self))

    @property
    def safe(self):
        return self.__safe__

    @safe.setter
    def safe(self, v):
        self.__safe__ = v

    @property
    def schemes(self):
        return self.url.scheme

    @property
    def netloc(self):
        return self.url.netloc

    @property
    def pages(self):
        """Returns a list of pages"""
        return self.__pages__

    @property
    def path(self):
        """
        Returns str of the Path
        """
        return self.url.path

    @property
    def queries_dict(self):
        return self.__query__

    @property
    def queries(self):
        return self.url.query

    @property
    def fragments(self):
        return self.url.fragement


    def __str__(self):
        """
        return str object
        """
        return urlunparse((self.__scheme__,
                        self.__hostname__,
                        self._page_gen(),
                        str(),
                        self._query_gen(),
                        self.__fragment__))

    def _page_gen(self):
        """
        Generates The String for pages
        """
        track = ""
        for page in self.__pages__:
            track += "/{page}".format(page=page)
        return track

    def _query_gen(self):
        """Generates The String for queries"""
        return urlencode(self.__query__, safe=self.safe, querydelimiter=self.__querydelimiter__)

    def hostname(self, hostname):
        self.__hostname__ = hostname
        return self

    def scheme(self, scheme):
        self.__scheme__ = scheme
        return self

    def page(self, *args):
        """
        Pages takes *args and adds pages in order
        """
        for arg in args:
            self.__pages__.append(arg)
        return self

    def query(self, listdelimiter="+", safe="", **kwargs):
        """
        Url queries

        :param listdelimiter: Specifies what list delimiter should be
        :param safe: string that includes all the characters that should not be ignored

        Kwargs (Since its a dictionary) are not ordered. You must call the
        method again if you absolutely need one query
        after another or vice versa.

        """
        safe = safe if safe else self.safe
        for arg in list(kwargs.keys()):
            if (isinstance(kwargs[arg], list)
                    or isinstance(kwargs[arg], tuple)
                    or isinstance(kwargs[arg], set)):
                items = [quote_plus(str(x), safe=safe) for x in kwargs[arg]]
                self.__query__.update({arg: listdelimiter.join(items)})
            else:
                self.__query__.update({arg: kwargs.get(arg)})

        return self

    def fragment(self, text):
        """
        Allows for fragments at the end of the url
        """
        self.__fragment__ = text
        return self

