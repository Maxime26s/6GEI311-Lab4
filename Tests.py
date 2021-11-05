import unittest
from Server import Database, Lab4HTTPRequestHandler
from socketserver import TCPServer
from http.server import SimpleHTTPRequestHandler
from unittest.mock import Mock
from io import BytesIO as IO
import json
from TwitterAPI import TwitterAPI


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
        SimpleHTTPRequestHandler.do_GET = Mock(return_value=200)
        f = open("testdata.json")
        t = f.read()
        TwitterAPI.query_twitter_api = Mock(return_value=json.loads(t))
        f.close()
        self.server = MockServer(('0.0.0.0', 8888), Lab4HTTPRequestHandler)

    def tearDown(self):
        self.server = None

    def test_route_search(self):
        self.server.handler.path = "/"
        self.server.handler.do_GET()
        self.assertEqual("Search.html", self.server.handler.path)

    def test_route_display(self):
        self.server.handler.path = "/queryTwitter"
        self.server.handler.do_GET()
        self.assertEqual("Display.html", self.server.handler.path)

    def test_route_invalid_path(self):
        self.server.handler.path = "/fdsafdsa"
        self.server.handler.do_GET()
        self.assertEqual("Search.html", self.server.handler.path)


class TestTwitterAPI(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
