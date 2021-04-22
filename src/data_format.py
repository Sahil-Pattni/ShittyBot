# Data manipulation
from sklearn.model_selection import train_test_split

# Tensorflow for LSTM
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

import re

import pickle

def clean(text):
    # regex = "[?!.:/|\\';\"\[\]{}<>,]+"
    regex = '[?!.,]+'
    text = re.sub(regex, '', text.lower())
    return f'<start> {text.strip()} <end>'


def tokenize(data):
    tokenizer = Tokenizer(oov_token='<OOV>', filters='')
    tokenizer.fit_on_texts(data)

    tensor = tokenizer.texts_to_sequences(data)
    tensor = pad_sequences(tensor, padding='post')

    return tensor, tokenizer


def get_train_data(filepath='data/message_log.pkl'):
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    
    X_orig, y_orig = data

    # Clean
    X = [clean(text) for text in X_orig]
    y = [clean(text) for text in y_orig]


    X, Xlang = tokenize(X)
    y, ylang = tokenize(y)

    return X, y, Xlang, ylang


    