from unittest import TestCase

from yql.utils import get_http_method


class UtilitiesTest(TestCase):
    def test_finds_get_method_for_select_query(self):
        self.assertEqual(get_http_method("SELECT foo"), "GET")

    def test_finds_get_method_for_select_query_with_leading_space(self):
        self.assertEqual(get_http_method(" SELECT foo"), "GET")

    def test_finds_get_method_for_lowercase_select_query(self):
        self.assertEqual(get_http_method("select foo"), "GET")

    def test_finds_post_method_for_insert_query(self):
        self.assertEqual(get_http_method("INSERT into"), "POST")

    def test_finds_post_method_for_multiline_insert_query(self):
        query = """
        INSERT INTO yql.queries.query (name, query)
        VALUES ("weather", "SELECT * FROM weather.forecast
            WHERE location=90210")
            """
        self.assertEqual(get_http_method(query), "POST")

    def test_finds_put_method_for_update_query(self):
        self.assertEqual(get_http_method("update foo"), "PUT")

    def test_finds_post_method_for_delete_query(self):
        self.assertEqual(get_http_method("DELETE from"), "POST")

    def test_finds_post_method_for_lowercase_delete_query(self):
        self.assertEqual(get_http_method("delete from"), "POST")

    def test_finds_get_method_for_show_query(self):
        self.assertEqual(get_http_method("SHOW tables"), "GET")

    def test_finds_get_method_for_describe_query(self):
        self.assertEqual(get_http_method("DESC tablename"), "GET")
