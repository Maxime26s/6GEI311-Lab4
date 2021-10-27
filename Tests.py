import unittest
from Server import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database()

    def tearDown(self):
        self.db = None

    def test_load_tweets_returns_list_on_error(self):
        self.db.tweets = 5
        self.assertTrue(type(self.db.load_tweets()) is list)
        self.assertEqual(self.db.load_tweets(), [])

    def test_can_load_tweets_default(self):
        self.assertEqual(self.db.load_tweets(), [])
     
    def test_can_load_tweets_mocked_db(self):
        self.db.tweets = ["tweet1", "tweet2"]
        self.assertEqual(self.db.load_tweets().count, 2)


class TestServer(unittest.TestCase):
    pass


class TestTwitterAPI(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()