import unittest

import requests
from requests.models import Response
from Server import Database, Lab4HTTPRequestHandler
from socketserver import TCPServer
from http.server import SimpleHTTPRequestHandler
from unittest.mock import MagicMock
from io import BytesIO as IO
import json
from TwitterAPI import BEARER_TOKEN, TwitterAPI


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database()

    def tearDown(self):
        self.db = None

    def test_load_tweets_returns_empty_list_on_error(self):
        self.db.tweets = 5
        self.assertTrue(type(self.db.load_tweets()) is list)
        self.assertEqual(self.db.load_tweets(), [])

    def test_can_load_tweets_default(self):
        self.assertEqual(self.db.load_tweets(), [])

    def test_can_load_tweets_mocked_db(self):
        self.db.tweets = [{"tweet1": "test"}, {"tweet2": "test"}]
        self.assertEqual(len(self.db.load_tweets()), 2)

    def test_can_save_tweets(self):
        self.assertEqual(len(self.db.tweets), 0)
        self.db.save_tweets([{"tweet1": "test"}, {"tweet2": "test"}])
        self.assertEqual(len(self.db.tweets), 2)

    def test_save_invalid_tweets(self):
        self.assertEqual(len(self.db.tweets), 0)
        self.db.save_tweets(5)
        self.db.save_tweets("invalid tweet")
        self.assertEqual(len(self.db.tweets), 0)


class MockRequest(object):
    def makefile(self, *args, **kwargs):
        return IO(b"GET /")

    def sendall(self, *args, **kwargs):
        return


class MockServer(object):
    def __init__(self, ip_port, Handler):
        self.handler = Handler(MockRequest(), ip_port, self)


class TestServer(unittest.TestCase):
    def setUp(self):
        SimpleHTTPRequestHandler.do_GET = MagicMock(return_value=200)

    def test_route_search(self):
        self.server = MockServer(('0.0.0.0', 8888), Lab4HTTPRequestHandler)
        self.server.handler.path = "/"
        self.server.handler.do_GET()
        self.assertEqual("Search.html", self.server.handler.path)

    def test_route_display(self):
        f = open("testdata.json")
        t = f.read()
        f.close()
        self.query_twitter_api = TwitterAPI.query_twitter_api
        TwitterAPI.query_twitter_api = MagicMock(return_value=json.loads(t))
        self.server = MockServer(('0.0.0.0', 8888), Lab4HTTPRequestHandler)
        self.server.handler.path = "/queryTwitter?query=test"
        self.server.handler.do_GET()
        self.assertEqual("Display.html", self.server.handler.path)
        TwitterAPI.query_twitter_api = self.query_twitter_api

    def test_route_invalid_path(self):
        self.server = MockServer(('0.0.0.0', 8888), Lab4HTTPRequestHandler)
        self.server.handler.path = "/fdsafdsa"
        self.server.handler.do_GET()
        self.assertEqual("Search.html", self.server.handler.path)

    def test_invalid_json_data_returned(self):
        self.query_twitter_api = TwitterAPI.query_twitter_api
        TwitterAPI.query_twitter_api = MagicMock(
            return_value={'errors': [{'parameters': {'query': ['']}, 'message': "Invalid 'query': ''. 'query' must be a non-empty string"}], 'title': 'Invalid Request', 'detail': 'One or more parameters to your request was invalid.', 'type': 'https://api.twitter.com/2/problems/invalid-request'})
        self.server = MockServer(('0.0.0.0', 8888), Lab4HTTPRequestHandler)
        self.server.handler.path = "/queryTwitter"
        self.server.handler.do_GET()
        self.assertEqual("Display.html", self.server.handler.path)
        TwitterAPI.query_twitter_api = self.query_twitter_api

    def test_search_empty_query(self):
        self.query_twitter_api = TwitterAPI.query_twitter_api
        TwitterAPI.query_twitter_api = MagicMock(
            return_value={'errors': [{'parameters': {'query': ['']}, 'message': "Invalid 'query': ''. 'query' must be a non-empty string"}], 'title': 'Invalid Request', 'detail': 'One or more parameters to your request was invalid.', 'type': 'https://api.twitter.com/2/problems/invalid-request'})
        self.server = MockServer(('0.0.0.0', 8888), Lab4HTTPRequestHandler)
        self.server.handler.path = "/queryTwitter?query="
        self.server.handler.do_GET()
        self.assertEqual("Display.html", self.server.handler.path)
        TwitterAPI.query_twitter_api = self.query_twitter_api


class TestTwitterAPI(unittest.TestCase):
    def test_request_no_header(self):
        headers = None
        url, params = TwitterAPI.create_twitter_url("data", 10)
        json_response = TwitterAPI.query_twitter_api(url, headers, params)
        self.assertEqual(json_response['error']['message'],
                         "Invalid 'headers': 'headers' must not be empty")

    def test_header_is_dictionary(self):
        headers = "not a dictionary"
        url, params = TwitterAPI.create_twitter_url("data", 10)
        json_response = TwitterAPI.query_twitter_api(url, headers, params)
        self.assertEqual(json_response['error']['message'],
                         "Invalid 'headers': 'headers' must not be a dictionary")

    def test_header_no_authorization(self):
        headers = {'Authorization': None}
        url, params = TwitterAPI.create_twitter_url("data", 10)
        json_response = TwitterAPI.query_twitter_api(url, headers, params)
        self.assertEqual(json_response['error']['message'],
                         "Invalid 'headers': 'Authorization' must not be None")

    def test_header_authorization_is_string(self):
        headers = {'Authorization': 0}
        url, params = TwitterAPI.create_twitter_url("data", 10)
        json_response = TwitterAPI.query_twitter_api(url, headers, params)
        self.assertEqual(json_response['error']['message'],
                         "Invalid 'headers': 'Authorization' must be a string")

    def test_header_empty_bearer_token(self):
        BEARER_TOKEN = ""
        headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
        url, params = TwitterAPI.create_twitter_url("data", 10)
        json_response = TwitterAPI.query_twitter_api(url, headers, params)
        self.assertEqual(json_response['error']['message'],
                         "Invalid 'headers': 'Authorization' must have a bearer token")

    def test_no_url(self):
        headers = TwitterAPI.create_twitter_headers()
        url, params = TwitterAPI.create_twitter_url("data", 10)
        url = None
        json_response = TwitterAPI.query_twitter_api(url, headers, params)
        self.assertEqual(json_response['error']['message'],
                         "Invalid 'url': 'url' must not be None")

    def test_url_is_string(self):
        headers = TwitterAPI.create_twitter_headers()
        url, params = TwitterAPI.create_twitter_url("data", 10)
        url = 0
        json_response = TwitterAPI.query_twitter_api(url, headers, params)
        self.assertEqual(json_response['error']['message'],
                         "Invalid 'url': 'url' must be a string")

    def test_empty_url(self):
        headers = TwitterAPI.create_twitter_headers()
        url, params = TwitterAPI.create_twitter_url("data", 10)
        url = ""
        json_response = TwitterAPI.query_twitter_api(url, headers, params)
        self.assertEqual(json_response['error']['message'],
                         "Invalid 'url': 'url' must not be empty")

    def test_no_params(self):
        headers = TwitterAPI.create_twitter_headers()
        url, params = TwitterAPI.create_twitter_url("data", 10)
        params = None
        json_response = TwitterAPI.query_twitter_api(url, headers, params)
        self.assertEqual(json_response['error']['message'],
                         "Invalid 'params': 'params' must not be None")

    def test_params_is_dictionary(self):
        headers = TwitterAPI.create_twitter_headers()
        url, params = TwitterAPI.create_twitter_url("data", 10)
        params = "not a dictionary"
        json_response = TwitterAPI.query_twitter_api(url, headers, params)
        self.assertEqual(json_response['error']['message'],
                         "Invalid 'params': 'params' must be a dictionary")

    def test_request_less_than_10_max_result(self):
        self.request = requests.request
        requests.request = MagicMock(
            return_value={'errors': [{'parameters': {'max_results': ['9']}, 'message': 'The `max_results` query parameter value [9] is not between 10 and 100'}], 'title': 'Invalid Request', 'detail': 'One or more parameters to your request was invalid.', 'type': 'https://api.twitter.com/2/problems/invalid-request'})
        headers = TwitterAPI.create_twitter_headers()
        url, params = TwitterAPI.create_twitter_url("data", 9)
        json_response = TwitterAPI.query_twitter_api(url, headers, params)
        self.assertEqual(json_response['error']['message'],
                         "Invalid 'params': 'max_results' must be between 10 and 100")
        requests.request = self.request

    def test_request_more_than_100_max_result(self):
        self.request = requests.request
        requests.request = MagicMock(
            return_value={'errors': [{'parameters': {'max_results': ['101']}, 'message': 'The `max_results` query parameter value [101] is not between 10 and 100'}], 'title': 'Invalid Request', 'detail': 'One or more parameters to your request was invalid.', 'type': 'https://api.twitter.com/2/problems/invalid-request'})
        headers = TwitterAPI.create_twitter_headers()
        url, params = TwitterAPI.create_twitter_url("data", 101)
        json_response = TwitterAPI.query_twitter_api(url, headers, params)
        self.assertEqual(json_response['error']['message'],
                         "Invalid 'params': 'max_results' must be between 10 and 100")
        requests.request = self.request


if __name__ == '__main__':
    unittest.main()
