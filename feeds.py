import feedparser
from feedparser.http import get

onion = 'http://www.theonion.com/feeds/rss'
xkcd = 'feed:https://xkcd.com/rss.xml'


def get_news():
    feed = feedparser.parse(xkcd)
    return feed.entries
