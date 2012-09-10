""""Utility functions"""
import re


METHOD_MAP = (
    ("insert", "POST"),
    ("update", "PUT"),
    ("delete", "POST"),
)
MULTI_PLUS = re.compile(r"\+{2,}")
MULTI_SPACE = re.compile(r" {2,}")


def get_http_method(query):
    """Work out if this should be GET, POST, PUT or DELETE"""
    lower_query = query.strip().lower()

    http_method = "GET"
    for method in METHOD_MAP:
        if method[0] in lower_query:
            http_method = method[1]
            break

    return http_method


def clean_url(url):
    """Cleans up a uri/url"""
    url = url.replace("\n", "")
    url = MULTI_PLUS.sub("+", url)
    return url


def clean_query(query):
    """Cleans up a query"""
    query = query.replace("\n", "")
    query = MULTI_SPACE.sub(" ", query)
    return query
