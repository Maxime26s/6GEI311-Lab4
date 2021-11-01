import unittest
from Server import Database, Lab4HTTPRequestHandler
from socketserver import TCPServer
from http.server import SimpleHTTPRequestHandler
from unittest.mock import MagicMock

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

class TestServer(unittest.TestCase):
    def setUp(self):
        SimpleHTTPRequestHandler.do_GET = MagicMock(return_value=200)

    def test_route_search(self):
        with TCPServer(('', 8081), Lab4HTTPRequestHandler) as tcp_server:
            request_handler = tcp_server.RequestHandlerClass
            request_handler.path = "/"
            request_handler.do_GET(request_handler)
            self.assertEqual("Search.html", request_handler.path)




class TestTwitterAPI(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()