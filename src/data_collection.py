# %%
# ----- SETUP ----- #
import re
import spacy
import emoji
import pandas as pd
from reddit import get_comments
from time import time


nlp = spacy.load("en_core_web_sm")


# ----- PUBLIC FUNCTIONS ----- #
def clean_string(text):
    # Hyperlinks, usernames, emojis
    regexes = ['https://[a-zA-Z.-/0-9_]+', 'u/[a-zA-Z0-9_]+', emoji.get_emoji_regexp()]

    for regex in regexes:
        text = re.sub(regex, '', text)
    text = text.lower().strip()
    
    doc = nlp(text)
    tokens = [t for t in doc if not (t.is_stop or t.is_punct)]
    return ' '.join(t.lemma_ for t in tokens)

if __name__ == '__main__':
    start = time()
    subbies = {
        'LIBERAL': ['DankLeft', 'LateStageCapitalism', 'PoliticalHumor'],
        'CONSERVATIVE': ['Conservative', 'republican', 'ConservativesOnly', 'WalkAway'],
        'NEUTRAL': ['Funny', 'InterestingAsFuck']
    }

    data = []
    limit = 200

    for category, subs in subbies.items():
        sublimit = int(limit/len(subs))
        for subreddit in subs:
            data.extend(get_comments(subreddit, category, limit=sublimit))
    
    end = time() - start
    print(f'Finished reading in comments in {end/60:,.2f} minutes.')
    print(f"I have {len(data):,} comments")
    df = pd.DataFrame(data)
    df.columns = ['comment', 'score']
    df['comment'] = df['comment'].apply(clean_string)
    df.to_feather('/Users/sloth_mini/Documents/Discord_Bot/data/political_comments.ftr')
    print(f'Finished writing out in {((time()-start)-end)/60:.2f} minutes.')

