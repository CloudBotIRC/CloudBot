class CaseInsensitiveDict(dict):
    """
    dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = {}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)
    """

    def get(self, k, d=None):  # real signature unknown; restored from __doc__
        """ D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None. """
        return super().get(k.lower() if k is not None else k, d)

    def pop(self, k, d=None):  # real signature unknown; restored from __doc__
        """
        D.pop(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised
        """
        return super().pop(k.lower() if k is not None else k, d)

    def setdefault(self, k, d=None):  # real signature unknown; restored from __doc__
        """ D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D """
        return super().setdefault(k.lower() if k is not None else k, d)

    def __contains__(self, k):  # real signature unknown
        """ True if D has a key k, else False. """
        return super().__contains__(k.lower() if k is not None else k)

    def __delitem__(self, k):  # real signature unknown
        """ Delete self[key]. """
        return super().__delitem__(k.lower() if k is not None else k)

    def __getitem__(self, k):  # real signature unknown; restored from __doc__
        """ x.__getitem__(y) <==> x[y] """
        return super().__getitem__(k.lower() if k is not None else k)

    def __setitem__(self, k, v):  # real signature unknown
        """ Set self[key] to value. """
        return super().__setitem__(k.lower() if k is not None else k, v)
