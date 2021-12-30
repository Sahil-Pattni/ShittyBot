import praw
import os
from random import randint


env = os.environ
reddit = praw.Reddit(
    client_id=env['REDDIT_KEY'],
    client_secret=env['REDDIT_SECRET'],
    user_agent='ML BOT')


def get_joke():
    sub = reddit.subreddit('jokes')
    jokes = list(sub.hot(limit=100))
    post = jokes[randint(0, len(jokes)-1)]
    return post.title, post.selftext


print(get_joke())
