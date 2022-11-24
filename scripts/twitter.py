#!/usr/bin/env python3

import os
import tweepy

class Client:
    def __init__(self):
        self.api = tweepy.API(tweepy.OAuth1UserHandler(
           os.getenv('CONSUMER_KEY'),
           os.getenv('CONSUMER_SECRET'),
           os.getenv('ACCESS_TOKEN'),
           os.getenv('ACCESS_TOKEN_SECRET'),
        ))

if __name__=='__main__':
    cli = Client()
    tws = cli.api.home_timeline()
    print(tws[0].text)

