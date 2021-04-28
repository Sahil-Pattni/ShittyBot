import os
import praw

env = os.environ
API_KEY = env.get('REDDIT_API')
SECRET = env.get('REDDIT_SECRET')

# Initialize Reddit instance
reddit = praw.Reddit(
    client_id=API_KEY,
    client_secret=SECRET,
    user_agent = 'ML BOT',
)

def get_comments(sub, orientation, limit=300):
    sub = reddit.subreddit(sub)
    comments = []
    for post in sub.hot(limit=limit):
        post.comment_sort = 'top'
        current_comments = post.comments.list()
        for c in current_comments:
            if isinstance(c, praw.models.reddit.comment.Comment):
                comm = c.body
                if comm != '[deleted]' and comm != '[removed]':
                    comments.append([comm, orientation])
    return comments
