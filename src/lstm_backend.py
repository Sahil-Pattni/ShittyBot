
# Data manipulation
from sklearn.model_selection import train_test_split

# Tensorflow for LSTM
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Other imports
import pandas as pd
FILEPATH = '/Users/sloth_mini/Documents/Discord_Bot/data/political_comments.ftr'


def tokenize(X, tokenizer, maxlen=None):
    X = tokenizer.texts_to_sequences(X)
    X = pad_sequences(X, padding='post', maxlen=maxlen)
    return X


def get_train_test_data(split=0.2):
    data = pd.read_feather(FILEPATH)
    data.comment = data.comment.str.replace('\n', '') # temporary
    X = data['comment'].to_list()
    y = pd.get_dummies(data['score'], prefix='orientation_is')

    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(X)
    X = tokenize(X, tokenizer)
    

    return train_test_split(X, y, test_size=split), tokenizer