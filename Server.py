from http.server import SimpleHTTPRequestHandler
from TwitterAPI import TwitterAPI
from urllib.parse import urlparse
from urllib.parse import parse_qs
from http import HTTPStatus


class Database:
    tweets = []

    def __init__(self):
        self.tweets = []

    def save_tweets(self, new_tweets):
        if type(new_tweets) is not list:
            return
        self.tweets.extend(new_tweets)

    def load_tweets(self):
        if type(self.tweets) is not list:
            self.tweets = []
        return self.tweets


class Lab4HTTPRequestHandler(SimpleHTTPRequestHandler):
    db = Database()

    def do_GET(self):
        if self.path == '/':
            self.route_search()
        elif self.path.startswith('/queryTwitter'):
            self.route_display()
        else:
            self.route_search()

    def route_search(self):
        self.path = 'Search.html'
        return SimpleHTTPRequestHandler.do_GET(self)

    def route_display(self):
        data = ''

        query_components = parse_qs(urlparse(self.path).query)
        if 'query' in query_components:
            data = query_components['query'][0]

        if data != '':
            headers = TwitterAPI.create_twitter_headers()
            url, params = TwitterAPI.create_twitter_url(data)
            json_response = TwitterAPI.query_twitter_api(url, headers, params)
            print(json_response)
            try:
                tweets = json_response['data']

                # Assume that right here, we save the tweets into a SQL databases
                self.db.save_tweets(tweets)
            except:
                print("Invalid json returned")
        else:
            print("No data requested.")

        # Assume that right here, we load the tweets from a SQL database
        all_tweets = self.db.load_tweets()

        tweets_to_display = ''
        for tweet in all_tweets:
            tweets_to_display += '<div> <li>' + tweet['text'] + '</li> </div>'

        text_to_display = ''
        with open('Display.html', 'r') as file:
            text_to_display = f"{file.read()}".format(**locals())

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.wfile.write(text_to_display.encode('utf-8'))
        self.wfile.close()

        self.path = 'Display.html'
