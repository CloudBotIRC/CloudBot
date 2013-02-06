from xml.dom import minidom

# extremely boring dom parsing ahead. Consider yourself warned.


# The reason for the uri arg is that the xml returned from lookups do not
# contain the href uri of the thing that was looked up. However, when an
# element is encountered that is NOT the root of a query, it DOES contain
# the href. We pass it in so the returned data will have the same format
# always
def parse_lookup_doc(src, uri=None):
    doc = minidom.parse(src)
    root = doc.documentElement

    if root.nodeName == "artist":
        return {"type": "artist", "result": parse_artist(root, uri)}
    elif root.nodeName == "album":
        return {"type": "album", "result": parse_album(root, uri)}
    elif root.nodeName == "track":
        return {"type": "track", "result": parse_track(root, uri)}
    else:
        raise Exception("unknown node type! " + root.nodeName) # fixme: proper exception here


def parse_search_doc(src):
    doc = minidom.parse(src)
    root = doc.documentElement

    if root.nodeName == "artists":
        return parse_artist_search(root)
    elif root.nodeName == "albums":
        return parse_album_search(root)
    elif root.nodeName == "tracks":
        return parse_track_search(root)
    else:
        raise Exception("unknown node type! " + root.nodeName) # fixme: proper exception here


def parse_artist(root, uri=None):
    ret = {}
    if uri or root.hasAttribute("href"):
        ret["href"] = uri or root.getAttribute("href")

    for name, elem in _nodes(root):
        if name == "name":
            ret["name"] = _text(elem)
        elif name == "albums":
            ret["albums"] = parse_albumlist(elem)

    return ret


def parse_artistlist(root):
    return map(parse_artist, _filter(root, "artist"))


def parse_albumlist(root):
    return map(parse_album, _filter(root, "album"))


def parse_tracklist(root):
    return map(parse_track, _filter(root, "track"))


def parse_album(root, uri=None):
    ret = {}
    if uri or root.hasAttribute("href"):
        ret["href"] = uri or root.getAttribute("href")

    for name, elem in _nodes(root):
        if name == "name":
            ret["name"] = _text(elem)
        elif name == "released":
            released = _text(elem)
            if released:
                ret["released"] = int(_text(elem))
        elif name == "id":
            if not "ids" in ret:
                ret["ids"] = []
            ret["ids"].append(parse_id(elem))
        elif name == "tracks":
            ret["tracks"] = parse_tracklist(elem)

    ret["artists"] = parse_artistlist(root)
    if len(ret["artists"]) == 1:
        ret["artist"] = ret["artists"][0]
    else:
        ret["artist"] = None


    # todo: availability stuff. RFH
    return ret


def parse_id(elem):
    ret = {"type": elem.getAttribute("type"),
           "id": _text(elem)}
    if elem.hasAttribute("href"):
        ret["href"] = elem.getAttribute("href")
    return ret


def parse_track(root, uri=None):
    ret = {}
    if uri or root.hasAttribute("href"):
        ret["href"] = uri or root.getAttribute("href")

    for name, elem in _nodes(root):
        if name == "name":
            ret["name"] = _text(elem)
        elif name == "disc-number":
            ret["disc-number"] = int(_text(elem))
        elif name == "track-number":
            ret["track-number"] = int(_text(elem))
        elif name == "length":
            ret["length"] = float(_text(elem))
        elif name == "popularity":
            ret["popularity"] = float(_text(elem))
        elif name == "album":
            ret["album"] = parse_album(elem)
        elif name == "id":
            if not "ids" in ret:
                ret["ids"] = []
            ret["ids"].append(parse_id(elem))

    ret["artists"] = parse_artistlist(root)

    # Following prop is there for backwards compat. It may be dropped in a
    # future version
    if ret["artists"]:
        ret["artist"] = ret["artists"][0]

    return ret


def parse_opensearch(root):
    ret = {}
    elems = root.getElementsByTagNameNS("http://a9.com/-/spec/opensearch/1.1/", "*")

    for name, elem in ((e.localName, e) for e in elems):
        if name == "Query":
            ret["term"] = elem.getAttribute("searchTerms")
            ret["start_page"] = int(elem.getAttribute("startPage"))
        elif name == "totalResults":
            ret["total_results"] = int(_text(elem))
        elif name == "startIndex":
            ret["start_index"] = int(_text(elem))
        elif name == "itemsPerPage":
            ret["items_per_page"] = int(_text(elem))

    return ret


def parse_album_search(root):
    # Note that the search result tags are not <search> tags or similar.
    # Instead they are normal <artists|albums|tracks> tags with extra
    # stuff from the opensearch namespace. That's why we cant just directly
    # return the result from parse_albumlist
    ret = parse_opensearch(root)
    ret["result"] = parse_albumlist(root)
    return ret


def parse_artist_search(root):
    ret = parse_opensearch(root)
    ret["result"] = parse_artistlist(root)
    return ret


def parse_track_search(root):
    ret = parse_opensearch(root)
    ret["result"] = parse_tracklist(root)
    return ret


def _nodes(elem):
    """return an generator yielding element nodes that are children
    of elem."""
    return ((e.nodeName, e) for e
            in elem.childNodes
            if e.nodeType==e.ELEMENT_NODE)


def _text(elem):
    """Returns a concatenation of all text nodes that are children
    of elem (roughly what elem.textContent does in web dom"""
    return "".join((e.nodeValue for e
                    in elem.childNodes
                    if e.nodeType==e.TEXT_NODE))


def _filter(elem, filtername):
    """Returns a generator yielding all child nodes with the nodeName name"""
    return (elem for (name, elem)
            in _nodes(elem)
            if name == filtername)
