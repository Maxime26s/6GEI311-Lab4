import requests

BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAACelVAEAAAAAOiyvYHxASNLJyh2jenBUHxzjC8g%3DPFMVueCi5yMa2xYqcSKaXlBHEo1b9eRDHf8zAjCeHi0IjdLUd9'


class TwitterAPI:
    @staticmethod
    def create_twitter_headers():
        headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
        return headers

    @staticmethod
    def create_twitter_url(keyword, max_results=10):
        search_url = 'https://api.twitter.com/2/tweets/search/recent'

        query_params = {
            'query': keyword,
            'max_results': max_results,
            'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
            'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,'
                            'public_metrics,referenced_tweets,reply_settings,source',
            'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
            'place.fields': 'full_name,id,country,country_code,geo,name,place_type',
            'next_token': {}
        }
        return search_url, query_params

    @staticmethod
    def query_twitter_api(url, headers, params):
        if headers == None:
            return {'error': {'message': "Invalid 'headers': 'headers' must not be empty"}}
        if type(headers) is not dict:
            return {'error': {'message': "Invalid 'headers': 'headers' must not be a dictionary"}}
        if len(headers['Authorization']) <= 7:
            return {'error': {'message': "Invalid 'headers': 'headers' must have a bearer token"}}
        if params['max_results'] < 10 or params['max_results'] > 100:
            return {'error': {'message': "Invalid 'max_results': 'max_results' must be between 10 and 100"}}
        if url == "":
            return {'error': {'message': "Invalid 'url': 'url' must not be empty"}}
        response = requests.request('GET', url, headers=headers, params=params)
        return response.json()
