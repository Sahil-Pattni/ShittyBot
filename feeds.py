import feedparser

onion = 'http://www.theonion.com/feeds/rss'

def get_news():
    feed = feedparser.parse(onion)
    return feed.entries