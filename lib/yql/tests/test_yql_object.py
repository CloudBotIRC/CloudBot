"""Tests for the YQL object"""

import json
from unittest import TestCase

from nose.tools import raises

from yql import YQLObj, NotOneError


data_dict = json.loads("""{"query":{"count":"3","created":"2009-11-20T12:11:56Z","lang":"en-US","updated":"2009-11-20T12:11:56Z","uri":"http://query.yahooapis.com/v1/yql?q=select+*+from+flickr.photos.search+where+text%3D%22panda%22+limit+3","diagnostics":{"publiclyCallable":"true","url":{"execution-time":"742","content":"http://api.flickr.com/services/rest/?method=flickr.photos.search&text=panda&page=1&per_page=10"},"user-time":"745","service-time":"742","build-version":"3805"},"results":{"photo":[{"farm":"3","id":"4117944207","isfamily":"0","isfriend":"0","ispublic":"1","owner":"12346075@N00","secret":"ce1f6092de","server":"2510","title":"Pandas"},{"farm":"3","id":"4118710292","isfamily":"0","isfriend":"0","ispublic":"1","owner":"12346075@N00","secret":"649632a3e2","server":"2754","title":"Pandas"},{"farm":"3","id":"4118698318","isfamily":"0","isfriend":"0","ispublic":"1","owner":"28451051@N02","secret":"ec0b508684","server":"2586","title":"fuzzy flowers (Kalanchoe tomentosa)"}]}}}""")
data_dict2 = json.loads("""{"query":{"count":"1","created":"2009-11-20T12:11:56Z","lang":"en-US","updated":"2009-11-20T12:11:56Z","uri":"http://query.yahooapis.com/v1/yql?q=select+*+from+flickr.photos.search+where+text%3D%22panda%22+limit+3","diagnostics":{"publiclyCallable":"true","url":{"execution-time":"742","content":"http://api.flickr.com/services/rest/?method=flickr.photos.search&text=panda&page=1&per_page=10"},"user-time":"745","service-time":"742","build-version":"3805"},"results":{"photo":{"farm":"3","id":"4117944207","isfamily":"0","isfriend":"0","ispublic":"1","owner":"12346075@N00","secret":"ce1f6092de","server":"2510","title":"Pandas"}}}}""")


yqlobj = YQLObj(data_dict)
yqlobj2 = YQLObj({})
yqlobj3 = YQLObj(data_dict2)


class YQLObjTest(TestCase):
    @raises(AttributeError)
    def test_yql_object_one(self):
        """Test that invalid query raises AttributeError"""
        yqlobj.query = 1

    def test_yqlobj_uri(self):
        """Test that the query uri is as expected."""
        self.assertEqual(yqlobj.uri, u"http://query.yahooapis.com/v1/yql?q=select+*+"\
                       "from+flickr.photos.search+where+text%3D%22panda%22+limit+3")

    def test_yqlobj_query(self):
        """Test retrieval of the actual query"""
        self.assertEqual(yqlobj.query, u'select * from flickr.photos.search '\
                                'where text="panda" limit 3')

    def test_yqlobj_count(self):
        """Check we have 3 records"""
        self.assertEqual(yqlobj.count, 3)

    def test_yqlobj_lang(self):
        """Check the lang attr."""
        self.assertEqual(yqlobj.lang, u"en-US")

    def test_yqlobj_results(self):
        """Check the results."""
        expected_results = {u'photo': [
                                {u'isfamily': u'0',
                                 u'title': u'Pandas',
                                 u'farm': u'3',
                                 u'ispublic': u'1',
                                 u'server': u'2510',
                                 u'isfriend': u'0',
                                 u'secret': u'ce1f6092de',
                                 u'owner': u'12346075@N00',
                                 u'id': u'4117944207'},
                                {u'isfamily': u'0',
                                 u'title': u'Pandas',
                                 u'farm': u'3',
                                 u'ispublic': u'1',
                                 u'server': u'2754',
                                 u'isfriend': u'0',
                                 u'secret': u'649632a3e2',
                                 u'owner': u'12346075@N00',
                                 u'id': u'4118710292'},
                                {u'isfamily': u'0',
                                 u'title': u'fuzzy flowers (Kalanchoe tomentosa)',
                                 u'farm': u'3',
                                 u'ispublic': u'1',
                                 u'server': u'2586',
                                 u'isfriend': u'0',
                                 u'secret': u'ec0b508684',
                                 u'owner': u'28451051@N02',
                                 u'id': u'4118698318'}
                            ]}
        self.assertEqual(yqlobj.results, expected_results)

    def test_yqlobj_raw(self):
        """Check the raw attr."""
        self.assertEqual(yqlobj.raw, data_dict.get('query'))

    def test_yqlobj_diagnostics(self):
        """Check the diagnostics"""
        self.assertEqual(yqlobj.diagnostics, data_dict.get('query').get('diagnostics'))

    def test_query_is_none(self):
        """Check query is None with no data."""
        self.assertTrue(yqlobj2.query is None)

    def test_rows(self):
        """Test we can iterate over the rows."""
        stuff = []
        for row in yqlobj.rows:
            stuff.append(row.get('server'))

        self.assertEqual(stuff, [u'2510', u'2754', u'2586'])

    @raises(NotOneError)
    def test_one(self):
        """Test that accessing one result raises exception"""
        yqlobj.one()

    def test_one_with_one_result(self):
        """Test accessing data with one result."""
        res = yqlobj3.one()
        self.assertEqual(res.get("title"), "Pandas")
