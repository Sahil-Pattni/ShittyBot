# %%
from bot import POLITICAL_CHANEL
from predictor import predict
import numpy as np
import pickle
import time
GENERAL_FILEPATH = '/Users/sloth_mini/Documents/Discord_Bot/data/message_log_general.pkl'
POLITICS_FILEPATH  = '/Users/sloth_mini/Documents/Discord_Bot/data/message_log_political-gentlemanly-discussion.pkl'


comments = pickle.load(open(GENERAL_FILEPATH, 'rb'))

# %%
start = time.time()
print(f'Analyzing {len(comments):,} comments.')
categs = ['CONSERVATIVE', 'LIBERAL', 'NEUTRAL']

tagged = {
    'CONSERVATIVE': [],
    'LIBERAL': [],
    'NEUTRAL': []
}

for c in comments:
    if len(c.split(' ')) < 3:
        continue
    try:
        scores = predict(c)
        if scores is not None:
            tag = categs[np.argmax(scores)]
            tagged[tag].append(c)
    except Exception as e:
        print(f'opps @ "{c}"')

print(f'Finished in {(time.time() - start)/60:,.2f} minutes')

# %%
for key, val in tagged.items():
    print(f'{key}: {len(val)}')
# %%
import matplotlib.pyplot as plt
# %%
