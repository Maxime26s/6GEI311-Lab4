import unittest
from Server import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database()

    def tearDown(self):
        self.db = None

    def test_load_tweets_returns_empty_array_on_error(self):
        self.db.tweets = 5
        self.assertTrue(type(self.db.load_tweets()) is list)


class TestServer(unittest.TestCase):
    pass


class TestTwitterAPI(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()